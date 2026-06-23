from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.core.security import validate_password_strength
from app.models.enums import Role


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=180)
    role: Role = Role.STUDENT
    team_id: int | None = None
    bio: str = Field(default="", max_length=2000)
    avatar_url: str | None = Field(default=None, max_length=500)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=72)

    @field_validator("password")
    @classmethod
    def password_is_strong(cls, value: str) -> str:
        return validate_password_strength(value)


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = Field(default=None, min_length=2, max_length=180)
    password: str | None = Field(default=None, min_length=8, max_length=72)
    role: Role | None = None
    team_id: int | None = None
    is_active: bool | None = None
    bio: str | None = Field(default=None, max_length=2000)
    avatar_url: str | None = Field(default=None, max_length=500)

    @field_validator("password")
    @classmethod
    def password_is_strong(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return validate_password_strength(value)


class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: Role
    is_active: bool
    team_id: int | None
    avatar_url: str | None
    bio: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserProfileRead(UserRead):
    team_name: str | None = None
    points: int = 0
    rank: int | None = None
    completed_tasks: int = 0
    badges: list[str] = Field(default_factory=list)
    statistics: dict = Field(default_factory=dict)
    achievements: list[dict] = Field(default_factory=list)
