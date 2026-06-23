from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.user import User
from app.routes.deps import get_current_user, get_db, require_admin
from app.schemas.statistics import DashboardStats, StatisticsOverview
from app.services.statistics import dashboard_for_user, statistics_overview

router = APIRouter(prefix="/statistics", tags=["statistics"])


@router.get("/dashboard", response_model=DashboardStats)
def dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    return dashboard_for_user(db, current_user)


@router.get("/overview", response_model=StatisticsOverview)
def overview(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> dict:
    return statistics_overview(db)

