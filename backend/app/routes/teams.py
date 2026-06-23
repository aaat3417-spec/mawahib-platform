from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.enums import Role
from app.models.team import Team
from app.models.user import User
from app.routes.deps import get_current_user, get_db, require_admin
from app.schemas.team import TeamCreate, TeamRead, TeamUpdate
from app.services.badges import evaluate_badges_for_user
from app.services.points import total_points

router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("", response_model=list[TeamRead])
def list_teams(db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> list[dict]:
    rows = (
        db.query(Team, func.count(User.id).label("member_count"))
        .outerjoin(User, User.team_id == Team.id)
        .group_by(Team.id)
        .order_by(Team.name.asc())
        .all()
    )
    return [{**TeamRead.model_validate(team).model_dump(), "member_count": count} for team, count in rows]


@router.post("", response_model=TeamRead, status_code=status.HTTP_201_CREATED)
def create_team(
    payload: TeamCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> dict:
    if db.query(Team).filter(Team.name == payload.name).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Team already exists.")
    team = Team(name=payload.name, description=payload.description)
    db.add(team)
    db.flush()
    if payload.leader_id:
        _assign_team_leader(db, team, payload.leader_id)
    db.commit()
    db.refresh(team)
    count = db.query(func.count(User.id)).filter(User.team_id == team.id).scalar() or 0
    return {**TeamRead.model_validate(team).model_dump(), "member_count": count}


@router.patch("/{team_id}", response_model=TeamRead)
def update_team(
    team_id: int,
    payload: TeamUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> dict:
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found.")
    updates = payload.model_dump(exclude_unset=True)
    if "leader_id" in updates:
        leader_id = updates.pop("leader_id")
        if leader_id is None:
            _clear_team_leader(db, team)
        else:
            _assign_team_leader(db, team, leader_id)
    for field, value in updates.items():
        setattr(team, field, value)
    db.commit()
    db.refresh(team)
    count = db.query(func.count(User.id)).filter(User.team_id == team.id).scalar() or 0
    return {**TeamRead.model_validate(team).model_dump(), "member_count": count}


@router.post("/{team_id}/join", response_model=TeamRead)
def join_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found.")
    if current_user.role != Role.STUDENT:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only students can join teams directly.")
    current_user.team_id = team_id
    db.commit()
    db.refresh(team)
    count = db.query(func.count(User.id)).filter(User.team_id == team.id).scalar() or 0
    return {**TeamRead.model_validate(team).model_dump(), "member_count": count}


@router.post("/{team_id}/leader/{user_id}", response_model=TeamRead)
def promote_team_leader(
    team_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> dict:
    team = db.get(Team, team_id)
    user = db.get(User, user_id)
    if not team or not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team or user not found.")
    _assign_team_leader(db, team, user.id)
    db.commit()
    db.refresh(team)
    evaluate_badges_for_user(db, user, total_points=total_points(db, user.id))
    db.commit()
    count = db.query(func.count(User.id)).filter(User.team_id == team.id).scalar() or 0
    return {**TeamRead.model_validate(team).model_dump(), "member_count": count}


def _clear_team_leader(db: Session, team: Team) -> None:
    if team.leader_id:
        previous = db.get(User, team.leader_id)
        if previous and previous.role == Role.TEAM_LEADER:
            previous.role = Role.STUDENT
    team.leader_id = None


def _assign_team_leader(db: Session, team: Team, user_id: int) -> None:
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active leader user not found.")
    if user.role in {Role.OWNER, Role.ADMIN}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Owners and admins cannot be assigned as team leaders.")
    if team.leader_id and team.leader_id != user.id:
        _clear_team_leader(db, team)
    existing_team = db.query(Team).filter(Team.leader_id == user.id, Team.id != team.id).first()
    if existing_team:
        existing_team.leader_id = None
    team.leader_id = user.id
    user.team_id = team.id
    user.role = Role.TEAM_LEADER
    db.flush()
    evaluate_badges_for_user(db, user, total_points=total_points(db, user.id))
