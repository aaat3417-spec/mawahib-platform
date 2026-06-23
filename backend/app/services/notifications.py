from sqlalchemy.orm import Session

from app.models.enums import NotificationType, Role
from app.models.notification import Notification
from app.models.user import User


def create_notification(
    db: Session,
    *,
    user_id: int,
    title: str,
    message: str,
    type: NotificationType,
    payload: dict | None = None,
) -> Notification:
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=type,
        payload=payload or {},
    )
    db.add(notification)
    return notification


def notify_users(
    db: Session,
    users: list[User],
    *,
    title: str,
    message: str,
    type: NotificationType,
    payload: dict | None = None,
) -> None:
    for user in users:
        create_notification(db, user_id=user.id, title=title, message=message, type=type, payload=payload)


def notify_roles(
    db: Session,
    roles: tuple[Role, ...],
    *,
    title: str,
    message: str,
    type: NotificationType,
    payload: dict | None = None,
) -> None:
    users = db.query(User).filter(User.role.in_(roles), User.is_active.is_(True)).all()
    notify_users(db, users, title=title, message=message, type=type, payload=payload)

