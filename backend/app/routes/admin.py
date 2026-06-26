from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.time import utc_now
from app.models.announcement import Announcement
from app.models.registration_request import RegistrationRequest
from app.models.submission import Submission
from app.models.task import Task
from app.models.team import Team
from app.models.user import User
from app.routes.deps import get_db, require_admin

router = APIRouter(prefix="/admin", tags=["admin"])
STARTED_AT = utc_now()


@router.get("/data-health")
def data_health(db: Session = Depends(get_db), _: User = Depends(require_admin)) -> dict:
    now = utc_now()
    return {
        "environment": settings.ENVIRONMENT,
        "database": _database_info(),
        "counts": {
            "users": db.query(User).count(),
            "teams": db.query(Team).count(),
            "tasks": db.query(Task).count(),
            "submissions": db.query(Submission).count(),
            "announcements": db.query(Announcement).count(),
            "registration_requests": db.query(RegistrationRequest).count(),
        },
        "started_at": STARTED_AT.isoformat(),
        "uptime_seconds": int((now - STARTED_AT).total_seconds()),
    }


@router.get("/export")
def export_data(db: Session = Depends(get_db), _: User = Depends(require_admin)) -> dict:
    return {
        "exported_at": utc_now().isoformat(),
        "users": [
            {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "is_active": user.is_active,
                "team_id": user.team_id,
                "created_at": _iso(user.created_at),
                "updated_at": _iso(user.updated_at),
            }
            for user in db.query(User).order_by(User.id.asc()).all()
        ],
        "teams": [
            {
                "id": team.id,
                "name": team.name,
                "description": team.description,
                "leader_id": team.leader_id,
                "team_code": team.team_code,
                "is_code_active": team.is_code_active,
                "created_at": _iso(team.created_at),
            }
            for team in db.query(Team).order_by(Team.id.asc()).all()
        ],
        "tasks": [
            {
                "id": task.id,
                "title": task.title,
                "category": task.category,
                "difficulty": task.difficulty,
                "deadline": _iso(task.deadline),
                "points": task.points,
                "is_required": task.is_required,
                "created_by_id": task.created_by_id,
            }
            for task in db.query(Task).order_by(Task.id.asc()).all()
        ],
        "submissions": [
            {
                "id": submission.id,
                "task_id": submission.task_id,
                "student_id": submission.student_id,
                "status": submission.status,
                "submitted_at": _iso(submission.submitted_at),
                "reviewed_at": _iso(submission.reviewed_at),
                "reviewed_by_id": submission.reviewed_by_id,
            }
            for submission in db.query(Submission).order_by(Submission.id.asc()).all()
        ],
        "announcements": [
            {
                "id": announcement.id,
                "title": announcement.title,
                "is_pinned": announcement.is_pinned,
                "scheduled_for": _iso(announcement.scheduled_for),
                "expires_at": _iso(announcement.expires_at),
                "created_by_id": announcement.created_by_id,
                "created_at": _iso(announcement.created_at),
            }
            for announcement in db.query(Announcement).order_by(Announcement.id.asc()).all()
        ],
        "registration_requests": [
            {
                "id": request.id,
                "email": request.email,
                "full_name": request.full_name,
                "team_id": request.team_id,
                "status": request.status,
                "created_at": _iso(request.created_at),
                "reviewed_at": _iso(request.reviewed_at),
                "reviewed_by_id": request.reviewed_by_id,
            }
            for request in db.query(RegistrationRequest).order_by(RegistrationRequest.id.asc()).all()
        ],
    }


def _database_info() -> dict:
    url = make_url(settings.DATABASE_URL)
    info = {
        "type": url.get_backend_name(),
        "driver": url.get_driver_name(),
    }
    if settings.is_sqlite:
        info["path"] = url.database
        info["persistent"] = bool(url.database and url.database.startswith("/var/data/"))
    else:
        info["host"] = url.host
        info["database"] = url.database
    return info


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value else None
