from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.time import utc_now
from app.models.announcement import Announcement
from app.models.enums import NotificationType
from app.models.user import User
from app.routes.deps import get_current_user, get_db, require_admin
from app.schemas.announcement import AnnouncementCreate, AnnouncementRead, AnnouncementUpdate
from app.services.notifications import notify_users

router = APIRouter(prefix="/announcements", tags=["announcements"])


@router.get("", response_model=list[AnnouncementRead])
def list_announcements(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[Announcement]:
    now = utc_now()
    return (
        db.query(Announcement)
        .filter((Announcement.scheduled_for.is_(None)) | (Announcement.scheduled_for <= now))
        .filter((Announcement.expires_at.is_(None)) | (Announcement.expires_at >= now))
        .order_by(Announcement.is_pinned.desc(), Announcement.created_at.desc())
        .all()
    )


@router.post("", response_model=AnnouncementRead, status_code=status.HTTP_201_CREATED)
def create_announcement(
    payload: AnnouncementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> Announcement:
    announcement = Announcement(**payload.model_dump(), created_by_id=current_user.id)
    db.add(announcement)
    db.flush()
    if not announcement.scheduled_for or announcement.scheduled_for <= utc_now():
        users = db.query(User).filter(User.is_active.is_(True)).all()
        notify_users(
            db,
            users,
            title="New announcement",
            message=announcement.title,
            type=NotificationType.NEW_ANNOUNCEMENT,
            payload={"announcement_id": announcement.id},
        )
    db.commit()
    db.refresh(announcement)
    return announcement


@router.patch("/{announcement_id}", response_model=AnnouncementRead)
def update_announcement(
    announcement_id: int,
    payload: AnnouncementUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> Announcement:
    announcement = db.get(Announcement, announcement_id)
    if not announcement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Announcement not found.")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(announcement, field, value)
    db.commit()
    db.refresh(announcement)
    return announcement


@router.delete("/{announcement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_announcement(
    announcement_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> None:
    announcement = db.get(Announcement, announcement_id)
    if not announcement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Announcement not found.")
    db.delete(announcement)
    db.commit()
