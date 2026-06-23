from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.models.enums import NotificationType, Role, TaskCategory
from app.models.submission import Submission
from app.models.task import Task
from app.models.user import User
from app.routes.deps import get_current_user, get_db, require_leader_or_admin
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.services.notifications import notify_roles

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskRead])
def list_tasks(
    category: TaskCategory | None = Query(default=None),
    required: bool | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[TaskRead]:
    query = db.query(Task).order_by(Task.deadline.asc())
    if category:
        query = query.filter(Task.category == category)
    if required is not None:
        query = query.filter(Task.is_required.is_(required))
    tasks = query.all()
    submission_statuses = {}
    for row in (
        db.query(Submission.task_id, Submission.status)
        .filter(Submission.student_id == current_user.id)
        .order_by(Submission.submitted_at.desc())
        .all()
    ):
        submission_statuses.setdefault(row.task_id, row.status)
    return [
        TaskRead.model_validate(task).model_copy(
            update={"submission_status": submission_statuses.get(task.id)}
        )
        for task in tasks
    ]


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_leader_or_admin),
) -> Task:
    task = Task(**payload.model_dump(), created_by_id=current_user.id)
    db.add(task)
    db.flush()
    notify_roles(
        db,
        (Role.STUDENT, Role.TEAM_LEADER),
        title="New task",
        message=f"A new {task.category} task is available: {task.title}.",
        type=NotificationType.NEW_TASK,
        payload={"task_id": task.id},
    )
    db.commit()
    db.refresh(task)
    return task


@router.get("/{task_id}", response_model=TaskRead)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskRead:
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")
    submission = (
        db.query(Submission)
        .filter(Submission.student_id == current_user.id, Submission.task_id == task_id)
        .order_by(Submission.submitted_at.desc())
        .first()
    )
    return TaskRead.model_validate(task).model_copy(update={"submission_status": submission.status if submission else None})


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_leader_or_admin),
) -> Task:
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")
    _ensure_can_manage_task(current_user, task)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_leader_or_admin),
) -> None:
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")
    _ensure_can_manage_task(current_user, task)
    db.delete(task)
    db.commit()


def _ensure_can_manage_task(user: User, task: Task) -> None:
    if user.role in {Role.OWNER, Role.ADMIN}:
        return
    if task.created_by_id == user.id:
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only manage tasks you created.")
