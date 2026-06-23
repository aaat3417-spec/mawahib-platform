from pydantic import BaseModel


class DashboardStats(BaseModel):
    welcome_message: str
    total_points: int
    current_rank: int | None
    completed_tasks: int
    weekly_progress: list[dict]
    recent_announcements: list[dict]
    upcoming_deadlines: list[dict]
    progress_percentage: float


class StatisticsOverview(BaseModel):
    total_members: int
    active_members: int
    completed_tasks: int
    submission_rate: float
    team_performance: list[dict]
    top_members: list[dict]
    weekly_activity: list[dict]

