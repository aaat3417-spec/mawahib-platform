from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import SubmissionStatus


class SubmissionReview(BaseModel):
    status: SubmissionStatus
    feedback: str = Field(default="", max_length=3000)
    excellent_work: bool = False
    helping_members_points: bool = False


class SubmissionRead(BaseModel):
    id: int
    task_id: int
    student_id: int
    link_url: str | None
    github_url: str | None
    notes: str
    file_path: str | None
    original_filename: str | None
    status: SubmissionStatus
    feedback: str
    reviewed_by_id: int | None
    reviewed_at: datetime | None
    submitted_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SubmissionDetailRead(SubmissionRead):
    task_title: str
    task_points: int
    student_name: str
    team_id: int | None = None
    team_name: str | None = None

