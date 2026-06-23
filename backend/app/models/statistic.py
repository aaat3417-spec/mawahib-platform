from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.time import utc_now
from app.db.base_class import Base


class StatisticSnapshot(Base):
    __tablename__ = "statistics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    metric_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    total_members: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    active_members: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed_tasks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    submission_rate: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    team_performance: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    top_members: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    weekly_activity: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
