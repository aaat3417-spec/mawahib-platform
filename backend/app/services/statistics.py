from datetime import datetime, timedelta

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.core.time import utc_day_start, utc_now, utc_today
from app.models.announcement import Announcement
from app.models.enums import Role, SubmissionStatus
from app.models.point import PointTransaction
from app.models.statistic import StatisticSnapshot
from app.models.submission import Submission
from app.models.task import Task
from app.models.team import Team
from app.models.user import User
from app.services.points import completed_task_count, total_points, user_rank


def team_leaderboard(db: Session, *, period: str = "all", limit: int = 10) -> list[dict]:
    since = _period_start(period)
    point_join = PointTransaction.user_id == User.id
    if since:
        point_join = and_(point_join, PointTransaction.created_at >= since)
    query = (
        db.query(
            Team.id,
            Team.name,
            func.coalesce(func.sum(PointTransaction.amount), 0).label("points"),
            func.count(func.distinct(User.id)).label("members"),
        )
        .outerjoin(User, and_(User.team_id == Team.id, User.is_active.is_(True)))
        .outerjoin(PointTransaction, point_join)
        .group_by(Team.id)
        .order_by(func.coalesce(func.sum(PointTransaction.amount), 0).desc(), Team.name.asc())
    )
    rows = query.limit(limit).all()
    return [
        {"rank": index + 1, "id": row.id, "name": row.name, "points": int(row.points), "members": row.members}
        for index, row in enumerate(rows)
    ]


def statistics_overview(db: Session) -> dict:
    seven_days_ago = utc_now() - timedelta(days=7)
    total_members = db.query(func.count(User.id)).scalar() or 0
    active_members = (
        db.query(func.count(func.distinct(Submission.student_id)))
        .filter(Submission.submitted_at >= seven_days_ago)
        .scalar()
        or 0
    )
    completed_tasks = (
        db.query(func.count(Submission.id)).filter(Submission.status == SubmissionStatus.ACCEPTED).scalar() or 0
    )
    total_submissions = db.query(func.count(Submission.id)).scalar() or 0
    accepted_submissions = completed_tasks
    submission_rate = round((accepted_submissions / total_submissions * 100), 2) if total_submissions else 0.0
    top_members = _top_members(db)
    weekly_activity = _weekly_activity(db)
    team_performance = team_leaderboard(db, limit=20)
    return {
        "total_members": total_members,
        "active_members": active_members,
        "completed_tasks": completed_tasks,
        "submission_rate": submission_rate,
        "team_performance": team_performance,
        "top_members": top_members,
        "weekly_activity": weekly_activity,
    }


def save_statistics_snapshot(db: Session) -> StatisticSnapshot:
    overview = statistics_overview(db)
    snapshot = StatisticSnapshot(
        metric_date=utc_today(),
        total_members=overview["total_members"],
        active_members=overview["active_members"],
        completed_tasks=overview["completed_tasks"],
        submission_rate=overview["submission_rate"],
        team_performance={"items": overview["team_performance"]},
        top_members=overview["top_members"],
        weekly_activity=overview["weekly_activity"],
    )
    db.add(snapshot)
    db.flush()
    return snapshot


def dashboard_for_user(db: Session, user: User) -> dict:
    total = total_points(db, user.id)
    completed = completed_task_count(db, user.id)
    required_task_count = db.query(func.count(Task.id)).filter(Task.is_required.is_(True)).scalar() or 0
    completed_required_count = (
        db.query(func.count(func.distinct(Submission.task_id)))
        .join(Task, Submission.task_id == Task.id)
        .filter(
            Submission.student_id == user.id,
            Submission.status == SubmissionStatus.ACCEPTED,
            Task.is_required.is_(True),
        )
        .scalar()
        or 0
    )
    progress_percentage = round((completed_required_count / required_task_count * 100), 2) if required_task_count else 0.0
    now = utc_now()
    recent_announcements = (
        db.query(Announcement)
        .filter((Announcement.scheduled_for.is_(None)) | (Announcement.scheduled_for <= now))
        .filter((Announcement.expires_at.is_(None)) | (Announcement.expires_at >= now))
        .order_by(Announcement.is_pinned.desc(), Announcement.created_at.desc())
        .limit(5)
        .all()
    )
    upcoming_deadlines = (
        db.query(Task)
        .filter(Task.deadline >= now)
        .order_by(Task.deadline.asc())
        .limit(5)
        .all()
    )
    return {
        "welcome_message": f"Welcome back, {user.full_name}.",
        "total_points": total,
        "current_rank": user_rank(db, user.id),
        "completed_tasks": completed,
        "weekly_progress": _weekly_activity(db, user_id=user.id),
        "recent_announcements": [
            {"id": item.id, "title": item.title, "is_pinned": item.is_pinned, "created_at": item.created_at.isoformat()}
            for item in recent_announcements
        ],
        "upcoming_deadlines": [
            {"id": item.id, "title": item.title, "deadline": item.deadline.isoformat(), "points": item.points}
            for item in upcoming_deadlines
        ],
        "progress_percentage": progress_percentage,
    }


def _top_members(db: Session) -> list[dict]:
    rows = (
        db.query(User.id, User.full_name, func.coalesce(func.sum(PointTransaction.amount), 0).label("points"))
        .outerjoin(PointTransaction, User.id == PointTransaction.user_id)
        .filter(User.is_active.is_(True))
        .filter(User.role.in_((Role.STUDENT, Role.TEAM_LEADER)))
        .group_by(User.id)
        .order_by(func.coalesce(func.sum(PointTransaction.amount), 0).desc())
        .limit(10)
        .all()
    )
    return [{"id": row.id, "full_name": row.full_name, "points": int(row.points)} for row in rows]


def _weekly_activity(db: Session, user_id: int | None = None) -> list[dict]:
    today = utc_today()
    output = []
    for offset in range(6, -1, -1):
        day = today - timedelta(days=offset)
        start = utc_day_start(day)
        end = start + timedelta(days=1)
        query = db.query(func.count(Submission.id)).filter(Submission.submitted_at >= start, Submission.submitted_at < end)
        if user_id:
            query = query.filter(Submission.student_id == user_id)
        output.append({"date": day.isoformat(), "submissions": query.scalar() or 0})
    return output


def _period_start(period: str) -> datetime | None:
    now = utc_now()
    if period == "weekly":
        return now - timedelta(days=7)
    if period == "monthly":
        return now - timedelta(days=30)
    return None
