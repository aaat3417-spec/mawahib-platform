from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.time import utc_now
from app.db.base_class import Base
from app.models.enums import RegistrationRequestStatus


class RegistrationRequest(Base):
    __tablename__ = "registration_requests"
    __table_args__ = (
        Index("ix_registration_requests_email", "email"),
        Index("ix_registration_requests_status", "status"),
        Index("ix_registration_requests_team_id", "team_id"),
        Index("ix_registration_requests_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(180), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    bio: Mapped[str] = mapped_column(Text, default="", nullable=False)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    status: Mapped[RegistrationRequestStatus] = mapped_column(
        Enum(RegistrationRequestStatus),
        default=RegistrationRequestStatus.PENDING,
        nullable=False,
    )
    admin_note: Mapped[str] = mapped_column(Text, default="", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    team = relationship("Team", back_populates="registration_requests")
    reviewed_by = relationship("User", foreign_keys=[reviewed_by_id])
