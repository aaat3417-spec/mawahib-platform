from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.badge import Badge, UserBadge
from app.models.user import User
from app.routes.deps import get_current_user, get_db, require_admin
from app.schemas.badge import BadgeAward, BadgeCreate, BadgeRead, UserBadgeRead
from app.services.badges import award_badge

router = APIRouter(prefix="/badges", tags=["badges"])


@router.get("", response_model=list[BadgeRead])
def list_badges(db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> list[Badge]:
    return db.query(Badge).order_by(Badge.name.asc()).all()


@router.post("", response_model=BadgeRead, status_code=status.HTTP_201_CREATED)
def create_badge(
    payload: BadgeCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> Badge:
    if db.query(Badge).filter(Badge.code == payload.code).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Badge code already exists.")
    badge = Badge(**payload.model_dump())
    db.add(badge)
    db.commit()
    db.refresh(badge)
    return badge


@router.post("/award", response_model=UserBadgeRead, status_code=status.HTTP_201_CREATED)
def award(
    payload: BadgeAward,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> UserBadge:
    if not db.get(User, payload.user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    user_badge = award_badge(db, user_id=payload.user_id, badge_code=payload.badge_code, awarded_by_id=current_user.id)
    if not user_badge:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Badge not found.")
    db.commit()
    db.refresh(user_badge)
    return user_badge

