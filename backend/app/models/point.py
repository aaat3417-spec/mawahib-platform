from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.time import utc_now
from app.db.base_class import Base
from app.models.enums import PointReason


class PointTransaction(Base):
    __tablename__ = "points"
    __table_args__ = (
        Index("ix_points_user_created_at", "user_id", "created_at"),
        Index("ix_points_submission_reason", "submission_id", "reason"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    submission_id: Mapped[int | None] = mapped_column(ForeignKey("submissions.id"), nullable=True, index=True)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[PointReason] = mapped_column(Enum(PointReason), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)

    user = relationship("User", back_populates="point_transactions", foreign_keys=[user_id])
    created_by = relationship("User", foreign_keys=[created_by_id])
    submission = relationship("Submission", back_populates="point_transactions")
