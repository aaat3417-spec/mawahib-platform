from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import TaskCategory, TaskDifficulty


class TaskBase(BaseModel):
    title: str = Field(min_length=3, max_length=220)
    description: str = Field(min_length=10)
    category: TaskCategory
    difficulty: TaskDifficulty
    estimated_hours: int = Field(default=1, ge=1, le=500)
    deadline: datetime
    points: int = Field(default=100, ge=1, le=10000)
    is_required: bool = True
    attachments: list[str] = Field(default_factory=list)

    @field_validator("attachments")
    @classmethod
    def attachments_are_http_urls(cls, value: list[str]) -> list[str]:
        for url in value:
            if not url.startswith(("http://", "https://", "/uploads/")):
                raise ValueError("Task attachments must be HTTP(S) URLs or /uploads/ paths.")
        return value


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=220)
    description: str | None = Field(default=None, min_length=10)
    category: TaskCategory | None = None
    difficulty: TaskDifficulty | None = None
    estimated_hours: int | None = Field(default=None, ge=1, le=500)
    deadline: datetime | None = None
    points: int | None = Field(default=None, ge=1, le=10000)
    is_required: bool | None = None
    attachments: list[str] | None = None

    @field_validator("attachments")
    @classmethod
    def attachments_are_http_urls(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return value
        for url in value:
            if not url.startswith(("http://", "https://", "/uploads/")):
                raise ValueError("Task attachments must be HTTP(S) URLs or /uploads/ paths.")
        return value


class TaskRead(TaskBase):
    id: int
    created_by_id: int | None
    created_at: datetime
    updated_at: datetime
    submission_status: str | None = None

    model_config = ConfigDict(from_attributes=True)
