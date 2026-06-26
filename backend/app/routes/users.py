from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.badge import UserBadge
from app.models.enums import PointReason, Role, SubmissionStatus
from app.models.point import PointTransaction
from app.models.submission import Submission
from app.models.task import Task
from app.models.team import Team
from app.models.user import User
from app.routes.deps import get_current_user, get_db, require_admin
from app.schemas.point import PointAward, PointRead
from app.schemas.user import UserCreate, UserProfileRead, UserRead, UserUpdate
from app.services.badges import evaluate_badges_for_user
from app.services.points import award_points, completed_task_count, total_points, user_rank

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserRead])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[User]:
    query = db.query(User).order_by(User.created_at.desc())
    if current_user.role == Role.TEAM_LEADER:
        query = query.filter(User.team_id == current_user.team_id)
    elif current_user.role not in {Role.OWNER, Role.ADMIN}:
        query = query.filter(User.id == current_user.id)
    return query.all()


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> User:
    if current_user.role != Role.OWNER and payload.role in {Role.OWNER, Role.ADMIN}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owners can create elevated accounts.")
    if db.query(User).filter(User.email == payload.email.lower()).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists.")
    if payload.team_id and not db.get(Team, payload.team_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found.")
    if payload.role == Role.TEAM_LEADER and not payload.team_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Team leaders must belong to a team.")

    user = User(
        email=payload.email.lower(),
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        role=payload.role,
        team_id=payload.team_id,
        bio=payload.bio,
        avatar_url=payload.avatar_url,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    evaluate_badges_for_user(db, user, total_points=0)
    db.commit()
    return user


@router.get("/me/profile", response_model=UserProfileRead)
def my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    return _profile_for_user(db, current_user)


@router.patch("/me", response_model=UserRead)
def update_me(
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:
    allowed_fields = {"full_name", "password", "bio", "avatar_url"}
    updates = payload.model_dump(exclude_unset=True)
    for field in set(updates) - allowed_fields:
        updates.pop(field, None)
    _apply_user_updates(current_user, updates)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    if current_user.role == Role.TEAM_LEADER and user.team_id != current_user.team_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot view users outside your team.")
    if current_user.role == Role.STUDENT and current_user.id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot view this user.")
    return user


@router.get("/{user_id}/profile", response_model=UserProfileRead)
def get_profile(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    if current_user.role == Role.TEAM_LEADER and user.team_id != current_user.team_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot view profiles outside your team.")
    if current_user.role == Role.STUDENT and current_user.id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Students can only view their own profile.")
    return _profile_for_user(db, user)


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> User:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    if current_user.role != Role.OWNER and (user.role == Role.OWNER or payload.role == Role.OWNER):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owners can manage owner accounts.")
    if current_user.role != Role.OWNER and (user.role == Role.ADMIN or payload.role == Role.ADMIN):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owners can manage admin accounts.")
    if current_user.id == user.id and payload.is_active is False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot deactivate your own account.")
    if current_user.id == user.id and payload.role is not None and payload.role != user.role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot change your own role.")
    _ensure_owner_safety(db, user, payload)
    if payload.team_id and not db.get(Team, payload.team_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found.")
    if payload.role == Role.TEAM_LEADER and not (payload.team_id or user.team_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Team leaders must belong to a team.")
    if payload.email and payload.email.lower() != user.email:
        existing = db.query(User).filter(User.email == payload.email.lower(), User.id != user.id).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists.")
    updates = payload.model_dump(exclude_unset=True)
    _apply_user_updates(user, updates)
    db.commit()
    db.refresh(user)
    evaluate_badges_for_user(db, user, total_points=total_points(db, user.id))
    db.commit()
    return user


@router.post("/{user_id}/points", response_model=PointRead, status_code=status.HTTP_201_CREATED)
def create_point_adjustment(
    user_id: int,
    payload: PointAward,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> PointTransaction:
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    if current_user.role != Role.OWNER and target.role in {Role.OWNER, Role.ADMIN}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owners can adjust elevated accounts.")
    if not target.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot award points to inactive users.")
    transaction = award_points(
        db,
        user_id=user_id,
        amount=payload.amount,
        reason=payload.reason or PointReason.ADMIN_ADJUSTMENT,
        description=payload.description,
        created_by_id=current_user.id,
    )
    db.commit()
    db.refresh(transaction)
    return transaction


def _apply_user_updates(user: User, updates: dict) -> None:
    if "email" in updates and updates["email"]:
        user.email = updates["email"].lower()
    if "password" in updates and updates["password"]:
        user.hashed_password = hash_password(updates["password"])
    for field in ("full_name", "role", "team_id", "is_active", "bio", "avatar_url"):
        if field in updates:
            setattr(user, field, updates[field])


def _ensure_owner_safety(db: Session, user: User, payload: UserUpdate) -> None:
    if user.role != Role.OWNER:
        return
    demoting_owner = payload.role is not None and payload.role != Role.OWNER
    deactivating_owner = payload.is_active is False
    if not (demoting_owner or deactivating_owner):
        return
    owner_count = db.query(func.count(User.id)).filter(User.role == Role.OWNER, User.is_active.is_(True)).scalar() or 0
    if owner_count <= 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one active owner is required.")


def _profile_for_user(db: Session, user: User) -> dict:
    points = total_points(db, user.id)
    achievements = (
        db.query(Submission, Task)
        .join(Task, Submission.task_id == Task.id)
        .filter(Submission.student_id == user.id, Submission.status == SubmissionStatus.ACCEPTED)
        .order_by(Submission.reviewed_at.desc().nullslast(), Submission.submitted_at.desc())
        .limit(10)
        .all()
    )
    badge_rows = (
        db.query(UserBadge)
        .filter(UserBadge.user_id == user.id)
        .join(UserBadge.badge)
        .order_by(UserBadge.awarded_at.desc())
        .all()
    )
    team_name = user.team.name if user.team else None
    excellent_count = (
        db.query(func.count(PointTransaction.id))
        .filter(PointTransaction.user_id == user.id, PointTransaction.reason == PointReason.EXCELLENT_WORK)
        .scalar()
        or 0
    )
    point_event_count = (
        db.query(func.count(PointTransaction.id)).filter(PointTransaction.user_id == user.id).scalar() or 0
    )
    return {
        **UserRead.model_validate(user).model_dump(),
        "team_name": team_name,
        "points": points,
        "rank": user_rank(db, user.id),
        "completed_tasks": completed_task_count(db, user.id),
        "badges": [row.badge.name for row in badge_rows],
        "statistics": {"excellent_work": excellent_count, "total_point_events": point_event_count},
        "achievements": [
            {
                "submission_id": submission.id,
                "task_title": task.title,
                "category": task.category,
                "points": task.points,
                "accepted_at": submission.reviewed_at.isoformat() if submission.reviewed_at else None,
            }
            for submission, task in achievements
        ],
    }
