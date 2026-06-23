from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TeamBase(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str = Field(default="", max_length=1500)


class TeamCreate(TeamBase):
    leader_id: int | None = None


class TeamUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=1500)
    leader_id: int | None = None


class TeamRead(TeamBase):
    id: int
    leader_id: int | None
    created_at: datetime
    member_count: int = 0

    model_config = ConfigDict(from_attributes=True)

