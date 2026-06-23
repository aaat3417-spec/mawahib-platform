from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AnnouncementBase(BaseModel):
    title: str = Field(min_length=3, max_length=220)
    body: str = Field(min_length=5)
    is_pinned: bool = False
    scheduled_for: datetime | None = None
    expires_at: datetime | None = None


class AnnouncementCreate(AnnouncementBase):
    pass


class AnnouncementUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=220)
    body: str | None = Field(default=None, min_length=5)
    is_pinned: bool | None = None
    scheduled_for: datetime | None = None
    expires_at: datetime | None = None


class AnnouncementRead(AnnouncementBase):
    id: int
    created_by_id: int | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

