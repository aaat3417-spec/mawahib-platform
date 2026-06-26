from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.core.time import utc_now
from app.models.enums import RegistrationRequestStatus, Role
from app.models.registration_request import RegistrationRequest
from app.models.team import Team
from app.models.user import User
from app.routes.deps import get_db, require_admin
from app.schemas.registration import (
    RegistrationAccept,
    RegistrationDecision,
    RegistrationRequestCreate,
    RegistrationRequestRead,
    TeamCodeStatusUpdate,
)
from app.schemas.team import TeamAdminRead
from app.services.team_codes import assign_unique_team_code

router = APIRouter(prefix="/registration", tags=["registration"])
admin_router = APIRouter(prefix="/admin", tags=["admin-registration"])


@router.post("/request", response_model=RegistrationRequestRead, status_code=status.HTTP_201_CREATED)
def create_registration_request(payload: RegistrationRequestCreate, db: Session = Depends(get_db)) -> dict:
    email = payload.email.lower()
    team = db.query(Team).filter(Team.team_code == payload.team_code).first()
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid team code.")
    if not team.is_code_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This team code is disabled.")
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists.")

    existing_request = (
        db.query(RegistrationRequest)
        .filter(RegistrationRequest.email == email)
        .order_by(RegistrationRequest.created_at.desc())
        .first()
    )
    if existing_request:
        if existing_request.status == RegistrationRequestStatus.PENDING:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Your request is pending review.")
        if existing_request.status == RegistrationRequestStatus.REJECTED:
            note = f" {existing_request.admin_note}" if existing_request.admin_note else ""
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Your request was rejected.{note}")
        if existing_request.status == RegistrationRequestStatus.ACCEPTED:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Your request was already accepted. Please login.")
        if existing_request.status == RegistrationRequestStatus.CHANGES_REQUESTED:
            note = f" {existing_request.admin_note}" if existing_request.admin_note else ""
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Changes requested by admin.{note}")

    request = RegistrationRequest(
        full_name=payload.full_name,
        email=email,
        hashed_password=hash_password(payload.password),
        bio=payload.bio,
        team_id=team.id,
        status=RegistrationRequestStatus.PENDING,
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return _request_detail(request)


@admin_router.get("/registration-requests", response_model=list[RegistrationRequestRead])
def list_registration_requests(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> list[dict]:
    requests = db.query(RegistrationRequest).order_by(RegistrationRequest.created_at.desc()).all()
    return [_request_detail(item) for item in requests]


@admin_router.post("/registration-requests/{request_id}/accept", response_model=RegistrationRequestRead)
def accept_registration_request(
    request_id: int,
    payload: RegistrationAccept | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> dict:
    request = _get_request(db, request_id)
    if request.status == RegistrationRequestStatus.ACCEPTED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request is already accepted.")
    if request.status == RegistrationRequestStatus.REJECTED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rejected requests cannot be accepted.")
    if db.query(User).filter(User.email == request.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists.")

    payload = payload or RegistrationAccept()
    if payload.role != Role.STUDENT:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Registration requests can only create student accounts.")
    team_id = payload.team_id or request.team_id
    if not db.get(Team, team_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found.")

    user = User(
        email=request.email,
        full_name=payload.full_name or request.full_name,
        hashed_password=request.hashed_password,
        role=Role.STUDENT,
        team_id=team_id,
        bio=request.bio,
        is_active=True,
    )
    db.add(user)
    request.status = RegistrationRequestStatus.ACCEPTED
    request.reviewed_by_id = current_user.id
    request.reviewed_at = utc_now()
    request.admin_note = "Accepted"
    db.commit()
    db.refresh(request)
    return _request_detail(request)


@admin_router.post("/registration-requests/{request_id}/reject", response_model=RegistrationRequestRead)
def reject_registration_request(
    request_id: int,
    payload: RegistrationDecision,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> dict:
    request = _get_request(db, request_id)
    if request.status == RegistrationRequestStatus.ACCEPTED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Accepted requests cannot be rejected.")
    request.status = RegistrationRequestStatus.REJECTED
    request.admin_note = payload.admin_note
    request.reviewed_by_id = current_user.id
    request.reviewed_at = utc_now()
    db.commit()
    db.refresh(request)
    return _request_detail(request)


@admin_router.post("/registration-requests/{request_id}/request-changes", response_model=RegistrationRequestRead)
def request_registration_changes(
    request_id: int,
    payload: RegistrationDecision,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> dict:
    request = _get_request(db, request_id)
    if request.status == RegistrationRequestStatus.ACCEPTED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Accepted requests cannot be changed.")
    request.status = RegistrationRequestStatus.CHANGES_REQUESTED
    request.admin_note = payload.admin_note
    request.reviewed_by_id = current_user.id
    request.reviewed_at = utc_now()
    db.commit()
    db.refresh(request)
    return _request_detail(request)


@admin_router.get("/teams", response_model=list[TeamAdminRead])
def list_admin_teams(db: Session = Depends(get_db), _: User = Depends(require_admin)) -> list[dict]:
    teams = db.query(Team).order_by(Team.name.asc()).all()
    return [_admin_team_detail(db, team) for team in teams]


@admin_router.post("/teams/{team_id}/regenerate-code", response_model=TeamAdminRead)
def regenerate_team_code(
    team_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> dict:
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found.")
    assign_unique_team_code(db, team)
    db.commit()
    db.refresh(team)
    return _admin_team_detail(db, team)


@admin_router.patch("/teams/{team_id}/code-status", response_model=TeamAdminRead)
def update_team_code_status(
    team_id: int,
    payload: TeamCodeStatusUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> dict:
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found.")
    team.is_code_active = payload.is_code_active
    db.commit()
    db.refresh(team)
    return _admin_team_detail(db, team)


def _get_request(db: Session, request_id: int) -> RegistrationRequest:
    request = db.get(RegistrationRequest, request_id)
    if not request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registration request not found.")
    return request


def _request_detail(request: RegistrationRequest) -> dict:
    return {
        "id": request.id,
        "full_name": request.full_name,
        "email": request.email,
        "bio": request.bio,
        "team_id": request.team_id,
        "team_name": request.team.name if request.team else None,
        "status": request.status,
        "admin_note": request.admin_note,
        "created_at": request.created_at,
        "reviewed_at": request.reviewed_at,
        "reviewed_by_id": request.reviewed_by_id,
    }


def _admin_team_detail(db: Session, team: Team) -> dict:
    member_count = db.query(User).filter(User.team_id == team.id).count()
    return {
        "id": team.id,
        "name": team.name,
        "description": team.description,
        "leader_id": team.leader_id,
        "created_at": team.created_at,
        "member_count": member_count,
        "team_code": team.team_code,
        "is_code_active": team.is_code_active,
    }
