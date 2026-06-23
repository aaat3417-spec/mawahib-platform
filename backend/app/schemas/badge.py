from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import BadgeCode


class BadgeCreate(BaseModel):
    code: BadgeCode
    name: str = Field(min_length=2, max_length=120)
    description: str = Field(default="", max_length=1000)
    icon: str = Field(default="award", max_length=80)


class BadgeRead(BadgeCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class BadgeAward(BaseModel):
    user_id: int
    badge_code: BadgeCode


class UserBadgeRead(BaseModel):
    id: int
    user_id: int
    badge_id: int
    awarded_by_id: int | None
    awarded_at: datetime

    model_config = ConfigDict(from_attributes=True)

