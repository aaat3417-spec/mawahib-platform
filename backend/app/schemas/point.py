from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import PointReason


class PointAward(BaseModel):
    amount: int = Field(ge=-10000, le=10000)
    reason: PointReason = PointReason.ADMIN_ADJUSTMENT
    description: str = Field(default="", max_length=500)


class PointRead(BaseModel):
    id: int
    user_id: int
    submission_id: int | None
    amount: int
    reason: PointReason
    description: str
    created_by_id: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

