from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.time import utc_now
from app.db.base_class import Base
from app.models.enums import SubmissionStatus


class Submission(Base):
    __tablename__ = "submissions"
    __table_args__ = (
        Index("ix_submissions_student_task_status", "student_id", "task_id", "status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), nullable=False, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    link_url: Mapped[str | None] = mapped_column(String(700), nullable=True)
    github_url: Mapped[str | None] = mapped_column(String(700), nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="", nullable=False)
    file_path: Mapped[str | None] = mapped_column(String(700), nullable=True)
    original_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[SubmissionStatus] = mapped_column(
        Enum(SubmissionStatus),
        default=SubmissionStatus.PENDING,
        nullable=False,
        index=True,
    )
    feedback: Mapped[str] = mapped_column(Text, default="", nullable=False)
    reviewed_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )

    task = relationship("Task", back_populates="submissions")
    student = relationship("User", back_populates="submissions", foreign_keys=[student_id])
    reviewed_by = relationship("User", back_populates="reviewed_submissions", foreign_keys=[reviewed_by_id])
    point_transactions = relationship("PointTransaction", back_populates="submission")
