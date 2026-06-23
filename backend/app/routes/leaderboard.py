from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.models.user import User
from app.routes.deps import get_current_user, get_db
from app.services.points import leaderboard_students
from app.services.statistics import team_leaderboard

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


@router.get("/students")
def students(
    period: str = Query(default="all", pattern="^(weekly|monthly|all)$"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[dict]:
    return leaderboard_students(db, period=period, limit=50)


@router.get("/teams")
def teams(
    period: str = Query(default="all", pattern="^(weekly|monthly|all)$"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[dict]:
    return team_leaderboard(db, period=period, limit=20)

