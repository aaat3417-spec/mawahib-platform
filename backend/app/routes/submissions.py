from urllib.parse import urlparse

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.time import utc_now
from app.models.enums import NotificationType, Role, SubmissionStatus
from app.models.submission import Submission
from app.models.task import Task
from app.models.user import User
from app.routes.deps import get_current_user, get_db, require_leader_or_admin
from app.schemas.submission import SubmissionDetailRead, SubmissionReview
from app.services.notifications import create_notification
from app.services.points import apply_submission_points, clear_submission_points
from app.services.storage import save_submission_upload

router = APIRouter(prefix="/submissions", tags=["submissions"])


@router.get("", response_model=list[SubmissionDetailRead])
def list_submissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    query = db.query(Submission).join(Submission.task).join(Submission.student).order_by(Submission.submitted_at.desc())
    if current_user.role == Role.STUDENT:
        query = query.filter(Submission.student_id == current_user.id)
    elif current_user.role == Role.TEAM_LEADER:
        query = query.filter(User.team_id == current_user.team_id)
    return [_submission_detail(item) for item in query.all()]


@router.post("/tasks/{task_id}", response_model=SubmissionDetailRead, status_code=status.HTTP_201_CREATED)
async def submit_task(
    task_id: int,
    link_url: str | None = Form(default=None),
    github_url: str | None = Form(default=None),
    notes: str = Form(default=""),
    file: UploadFile | None = File(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")
    if current_user.role not in {Role.STUDENT, Role.TEAM_LEADER}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only students and team leaders can submit work.")
    if not any([link_url, github_url, notes.strip(), file]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Submission content is required.")
    link_url = _normalize_optional_url(link_url, "link_url")
    github_url = _normalize_optional_url(github_url, "github_url")
    existing_open_submission = (
        db.query(Submission)
        .filter(
            Submission.task_id == task_id,
            Submission.student_id == current_user.id,
            Submission.status.in_((SubmissionStatus.PENDING, SubmissionStatus.ACCEPTED)),
        )
        .first()
    )
    if existing_open_submission:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This task already has a pending or accepted submission.",
        )

    file_path = None
    original_filename = None
    if file:
        file_path, original_filename = await save_submission_upload(file)

    submission = Submission(
        task_id=task_id,
        student_id=current_user.id,
        link_url=link_url,
        github_url=github_url,
        notes=notes,
        file_path=file_path,
        original_filename=original_filename,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return _submission_detail(submission)


@router.patch("/{submission_id}/review", response_model=SubmissionDetailRead)
def review_submission(
    submission_id: int,
    payload: SubmissionReview,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_leader_or_admin),
) -> dict:
    submission = db.get(Submission, submission_id)
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found.")
    if current_user.role == Role.TEAM_LEADER and submission.student.team_id != current_user.team_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot review submissions outside your team.")
    if submission.student_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot review your own submission.")

    previous_status = submission.status
    was_accepted = previous_status == SubmissionStatus.ACCEPTED
    if was_accepted:
        clear_submission_points(db, submission.id)
    submission.status = payload.status
    submission.feedback = payload.feedback
    submission.reviewed_by_id = current_user.id
    submission.reviewed_at = utc_now()
    db.flush()

    if payload.status == SubmissionStatus.ACCEPTED:
        apply_submission_points(
            db,
            submission=submission,
            reviewer_id=current_user.id,
            excellent_work=payload.excellent_work,
            helping_members_points=payload.helping_members_points,
            send_notification=previous_status != SubmissionStatus.ACCEPTED,
        )
    elif previous_status != payload.status:
        create_notification(
            db,
            user_id=submission.student_id,
            title="Submission update",
            message=f"Your submission for {submission.task.title} is now {payload.status}.",
            type=NotificationType.SUBMISSION_REJECTED,
            payload={"task_id": submission.task_id, "submission_id": submission.id, "status": payload.status.value},
        )

    db.commit()
    db.refresh(submission)
    return _submission_detail(submission)


def _submission_detail(submission: Submission) -> dict:
    return {
        **SubmissionDetailRead.model_validate(
            {
                **submission.__dict__,
                "task_title": submission.task.title,
                "task_points": submission.task.points,
                "student_name": submission.student.full_name,
                "team_id": submission.student.team_id,
                "team_name": submission.student.team.name if submission.student.team else None,
            }
        ).model_dump()
    }


def _normalize_optional_url(value: str | None, field_name: str) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    if not stripped:
        return None
    parsed = urlparse(stripped)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{field_name} must be an HTTP(S) URL.")
    if field_name == "github_url" and "github.com" not in parsed.netloc.lower():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="github_url must point to github.com.")
    return stripped
