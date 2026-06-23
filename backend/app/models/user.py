from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.time import utc_now
from app.db.base_class import Base
from app.models.enums import Role


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(180), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.STUDENT, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    team_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"), nullable=True, index=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    bio: Mapped[str] = mapped_column(Text, default="", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )

    team = relationship("Team", back_populates="members", foreign_keys=[team_id])
    created_tasks = relationship("Task", back_populates="created_by", foreign_keys="Task.created_by_id")
    submissions = relationship("Submission", back_populates="student", foreign_keys="Submission.student_id")
    reviewed_submissions = relationship(
        "Submission",
        back_populates="reviewed_by",
        foreign_keys="Submission.reviewed_by_id",
    )
    point_transactions = relationship("PointTransaction", back_populates="user", foreign_keys="PointTransaction.user_id")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    user_badges = relationship(
        "UserBadge",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="UserBadge.user_id",
    )
