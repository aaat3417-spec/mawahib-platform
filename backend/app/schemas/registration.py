from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.core.security import validate_password_strength
from app.models.enums import RegistrationRequestStatus, Role


class RegistrationRequestCreate(BaseModel):
    team_code: str = Field(min_length=4, max_length=32)
    full_name: str = Field(min_length=2, max_length=180)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    bio: str = Field(default="", max_length=2000)

    @field_validator("team_code")
    @classmethod
    def normalize_team_code(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("password")
    @classmethod
    def password_is_strong(cls, value: str) -> str:
        return validate_password_strength(value)


class RegistrationRequestRead(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    bio: str
    team_id: int
    team_name: str | None = None
    status: RegistrationRequestStatus
    admin_note: str
    created_at: datetime
    reviewed_at: datetime | None
    reviewed_by_id: int | None

    model_config = ConfigDict(from_attributes=True)


class RegistrationAccept(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=180)
    team_id: int | None = None
    role: Role = Role.STUDENT


class RegistrationDecision(BaseModel):
    admin_note: str = Field(default="", max_length=2000)


class TeamCodeStatusUpdate(BaseModel):
    is_code_active: bool
