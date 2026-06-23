from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.badge import Badge, UserBadge
from app.models.enums import BadgeCode, NotificationType, PointReason, Role, SubmissionStatus, TaskCategory
from app.models.point import PointTransaction
from app.models.submission import Submission
from app.models.task import Task
from app.models.user import User
from app.services.notifications import create_notification

DEFAULT_BADGES = [
    (BadgeCode.RESEARCHER, "Researcher", "Completed high-quality research tasks.", "book-open"),
    (BadgeCode.PROGRAMMER, "Programmer", "Completed programming challenges.", "code"),
    (BadgeCode.AI_EXPERT, "AI Expert", "Completed artificial intelligence tasks.", "brain"),
    (BadgeCode.LEADER, "Leader", "Serves as a team leader.", "users"),
    (BadgeCode.CONTRIBUTOR, "Contributor", "Consistently helps other members.", "heart-handshake"),
    (BadgeCode.TOP_STUDENT, "Top Student", "Reached an elite point total.", "trophy"),
]


def seed_badges(db: Session) -> None:
    existing = {badge.code for badge in db.query(Badge).all()}
    for code, name, description, icon in DEFAULT_BADGES:
        if code not in existing:
            db.add(Badge(code=code, name=name, description=description, icon=icon))


def award_badge(db: Session, *, user_id: int, badge_code: BadgeCode, awarded_by_id: int | None = None) -> UserBadge | None:
    badge = db.query(Badge).filter(Badge.code == badge_code).first()
    if not badge:
        return None
    existing = db.query(UserBadge).filter(UserBadge.user_id == user_id, UserBadge.badge_id == badge.id).first()
    if existing:
        return existing

    user_badge = UserBadge(user_id=user_id, badge_id=badge.id, awarded_by_id=awarded_by_id)
    db.add(user_badge)
    create_notification(
        db,
        user_id=user_id,
        title="Badge earned",
        message=f"You earned the {badge.name} badge.",
        type=NotificationType.BADGE_EARNED,
        payload={"badge_code": badge.code, "badge_name": badge.name},
    )
    return user_badge


def _accepted_count_for_category(db: Session, user_id: int, category: TaskCategory) -> int:
    return (
        db.query(func.count(Submission.id))
        .join(Task, Submission.task_id == Task.id)
        .filter(
            Submission.student_id == user_id,
            Submission.status == SubmissionStatus.ACCEPTED,
            Task.category == category,
        )
        .scalar()
        or 0
    )


def evaluate_badges_for_user(db: Session, user: User, *, total_points: int) -> None:
    if user.role == Role.TEAM_LEADER:
        award_badge(db, user_id=user.id, badge_code=BadgeCode.LEADER)

    if total_points >= 500:
        award_badge(db, user_id=user.id, badge_code=BadgeCode.TOP_STUDENT)

    if _accepted_count_for_category(db, user.id, TaskCategory.PROGRAMMING) >= 3:
        award_badge(db, user_id=user.id, badge_code=BadgeCode.PROGRAMMER)

    if _accepted_count_for_category(db, user.id, TaskCategory.RESEARCH) >= 3:
        award_badge(db, user_id=user.id, badge_code=BadgeCode.RESEARCHER)

    if _accepted_count_for_category(db, user.id, TaskCategory.ARTIFICIAL_INTELLIGENCE) >= 3:
        award_badge(db, user_id=user.id, badge_code=BadgeCode.AI_EXPERT)

    helping_count = (
        db.query(func.count(PointTransaction.id))
        .filter(
            PointTransaction.user_id == user.id,
            PointTransaction.reason == PointReason.HELPING_MEMBERS,
        )
        .scalar()
        or 0
    )
    if helping_count >= 3:
        award_badge(db, user_id=user.id, badge_code=BadgeCode.CONTRIBUTOR)

