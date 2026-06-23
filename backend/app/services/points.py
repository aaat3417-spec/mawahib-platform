from datetime import datetime, timedelta

from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session

from app.core.time import utc_now
from app.models.enums import NotificationType, PointReason, Role, SubmissionStatus
from app.models.point import PointTransaction
from app.models.submission import Submission
from app.models.user import User
from app.services.badges import evaluate_badges_for_user
from app.services.notifications import create_notification

TASK_COMPLETION_POINTS = 100
EXCELLENT_WORK_POINTS = 50
EXTRA_TASK_POINTS = 30
HELPING_MEMBERS_POINTS = 20
LATE_SUBMISSION_PENALTY = -20


def total_points(db: Session, user_id: int, since: datetime | None = None) -> int:
    query = db.query(func.coalesce(func.sum(PointTransaction.amount), 0)).filter(PointTransaction.user_id == user_id)
    if since:
        query = query.filter(PointTransaction.created_at >= since)
    return int(query.scalar() or 0)


def award_points(
    db: Session,
    *,
    user_id: int,
    amount: int,
    reason: PointReason,
    description: str,
    created_by_id: int | None = None,
    submission_id: int | None = None,
) -> PointTransaction:
    transaction = PointTransaction(
        user_id=user_id,
        amount=amount,
        reason=reason,
        description=description,
        created_by_id=created_by_id,
        submission_id=submission_id,
    )
    db.add(transaction)
    db.flush()
    user = db.get(User, user_id)
    if user:
        evaluate_badges_for_user(db, user, total_points=total_points(db, user_id))
    return transaction


def _has_submission_reason(db: Session, submission_id: int, reason: PointReason) -> bool:
    return (
        db.query(PointTransaction.id)
        .filter(PointTransaction.submission_id == submission_id, PointTransaction.reason == reason)
        .first()
        is not None
    )


def apply_submission_points(
    db: Session,
    *,
    submission: Submission,
    reviewer_id: int,
    excellent_work: bool,
    helping_members_points: bool,
    send_notification: bool = True,
) -> None:
    if submission.status != SubmissionStatus.ACCEPTED:
        return

    task = submission.task
    if not _has_submission_reason(db, submission.id, PointReason.TASK_COMPLETION):
        award_points(
            db,
            user_id=submission.student_id,
            amount=task.points,
            reason=PointReason.TASK_COMPLETION,
            description=f"Completed task: {task.title}",
            created_by_id=reviewer_id,
            submission_id=submission.id,
        )

    if not task.is_required and not _has_submission_reason(db, submission.id, PointReason.EXTRA_TASK):
        award_points(
            db,
            user_id=submission.student_id,
            amount=EXTRA_TASK_POINTS,
            reason=PointReason.EXTRA_TASK,
            description=f"Extra task bonus: {task.title}",
            created_by_id=reviewer_id,
            submission_id=submission.id,
        )

    if excellent_work and not _has_submission_reason(db, submission.id, PointReason.EXCELLENT_WORK):
        award_points(
            db,
            user_id=submission.student_id,
            amount=EXCELLENT_WORK_POINTS,
            reason=PointReason.EXCELLENT_WORK,
            description=f"Excellent work bonus: {task.title}",
            created_by_id=reviewer_id,
            submission_id=submission.id,
        )

    if helping_members_points and not _has_submission_reason(db, submission.id, PointReason.HELPING_MEMBERS):
        award_points(
            db,
            user_id=submission.student_id,
            amount=HELPING_MEMBERS_POINTS,
            reason=PointReason.HELPING_MEMBERS,
            description="Helped community members.",
            created_by_id=reviewer_id,
            submission_id=submission.id,
        )

    if submission.submitted_at > task.deadline and not _has_submission_reason(db, submission.id, PointReason.LATE_SUBMISSION):
        award_points(
            db,
            user_id=submission.student_id,
            amount=LATE_SUBMISSION_PENALTY,
            reason=PointReason.LATE_SUBMISSION,
            description=f"Late submission penalty: {task.title}",
            created_by_id=reviewer_id,
            submission_id=submission.id,
        )

    if send_notification:
        create_notification(
            db,
            user_id=submission.student_id,
            title="Submission accepted",
            message=f"Your submission for {task.title} was accepted.",
            type=NotificationType.SUBMISSION_ACCEPTED,
            payload={"task_id": task.id, "submission_id": submission.id},
        )


def clear_submission_points(db: Session, submission_id: int) -> int:
    deleted = (
        db.query(PointTransaction)
        .filter(PointTransaction.submission_id == submission_id)
        .delete(synchronize_session=False)
    )
    db.flush()
    return deleted


def completed_task_count(db: Session, user_id: int) -> int:
    return (
        db.query(func.count(func.distinct(Submission.task_id)))
        .filter(Submission.student_id == user_id, Submission.status == SubmissionStatus.ACCEPTED)
        .scalar()
        or 0
    )


def leaderboard_students(db: Session, *, period: str = "all", limit: int = 10) -> list[dict]:
    since = _period_start(period)
    point_join = PointTransaction.user_id == User.id
    if since:
        point_join = and_(point_join, PointTransaction.created_at >= since)
    query = (
        db.query(
            User.id,
            User.full_name,
            User.team_id,
            func.coalesce(func.sum(PointTransaction.amount), 0).label("points"),
        )
        .outerjoin(PointTransaction, point_join)
        .filter(User.is_active.is_(True))
        .filter(User.role.in_((Role.STUDENT, Role.TEAM_LEADER)))
        .group_by(User.id)
        .order_by(desc("points"), User.full_name.asc())
    )
    rows = query.limit(limit).all()
    return [
        {"rank": index + 1, "id": row.id, "full_name": row.full_name, "team_id": row.team_id, "points": int(row.points)}
        for index, row in enumerate(rows)
    ]


def user_rank(db: Session, user_id: int, *, period: str = "all") -> int | None:
    rankings = leaderboard_students(db, period=period, limit=10000)
    for row in rankings:
        if row["id"] == user_id:
            return row["rank"]
    return None


def _period_start(period: str) -> datetime | None:
    now = utc_now()
    if period == "weekly":
        return now - timedelta(days=7)
    if period == "monthly":
        return now - timedelta(days=30)
    return None
