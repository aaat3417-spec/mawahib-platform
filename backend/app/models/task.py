from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.time import utc_now
from app.db.base_class import Base
from app.models.enums import TaskCategory, TaskDifficulty


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(220), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[TaskCategory] = mapped_column(Enum(TaskCategory), nullable=False, index=True)
    difficulty: Mapped[TaskDifficulty] = mapped_column(Enum(TaskDifficulty), nullable=False)
    estimated_hours: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    points: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    is_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    attachments: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )

    created_by = relationship("User", back_populates="created_tasks", foreign_keys=[created_by_id])
    submissions = relationship("Submission", back_populates="task", cascade="all, delete-orphan")
