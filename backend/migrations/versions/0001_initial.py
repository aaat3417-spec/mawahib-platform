"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-23
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

role_enum = sa.Enum("OWNER", "ADMIN", "TEAM_LEADER", "STUDENT", name="role")
task_category_enum = sa.Enum(
    "PROGRAMMING",
    "RESEARCH",
    "ARTIFICIAL_INTELLIGENCE",
    "MATHEMATICS",
    "SCIENCE",
    "ENGLISH",
    "INNOVATION",
    name="taskcategory",
)
task_difficulty_enum = sa.Enum("BEGINNER", "INTERMEDIATE", "ADVANCED", "EXPERT", name="taskdifficulty")
submission_status_enum = sa.Enum("PENDING", "ACCEPTED", "NEEDS_REVISION", "REJECTED", name="submissionstatus")
point_reason_enum = sa.Enum(
    "TASK_COMPLETION",
    "EXCELLENT_WORK",
    "EXTRA_TASK",
    "HELPING_MEMBERS",
    "LATE_SUBMISSION",
    "ADMIN_ADJUSTMENT",
    name="pointreason",
)
badge_code_enum = sa.Enum(
    "RESEARCHER",
    "PROGRAMMER",
    "AI_EXPERT",
    "LEADER",
    "CONTRIBUTOR",
    "TOP_STUDENT",
    name="badgecode",
)
notification_type_enum = sa.Enum(
    "NEW_TASK",
    "SUBMISSION_ACCEPTED",
    "SUBMISSION_REJECTED",
    "NEW_ANNOUNCEMENT",
    "BADGE_EARNED",
    "RANK_CHANGED",
    name="notificationtype",
)


def upgrade() -> None:

    op.create_table(
        "teams",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("leader_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_teams_id", "teams", ["id"])
    op.create_index("ix_teams_leader_id", "teams", ["leader_id"])
    op.create_index("ix_teams_name", "teams", ["name"], unique=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=180), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role", role_enum, nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=True),
        sa.Column("avatar_url", sa.String(length=500), nullable=True),
        sa.Column("bio", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_foreign_key("fk_teams_leader_id_users", "teams", "users", ["leader_id"], ["id"])
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_role", "users", ["role"])
    op.create_index("ix_users_team_id", "users", ["team_id"])

    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=220), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("category", task_category_enum, nullable=False),
        sa.Column("difficulty", task_difficulty_enum, nullable=False),
        sa.Column("estimated_hours", sa.Integer(), nullable=False),
        sa.Column("deadline", sa.DateTime(timezone=True), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False),
        sa.Column("is_required", sa.Boolean(), nullable=False),
        sa.Column("attachments", sa.JSON(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_tasks_id", "tasks", ["id"])
    op.create_index("ix_tasks_title", "tasks", ["title"])
    op.create_index("ix_tasks_category", "tasks", ["category"])
    op.create_index("ix_tasks_deadline", "tasks", ["deadline"])

    op.create_table(
        "submissions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("task_id", sa.Integer(), sa.ForeignKey("tasks.id"), nullable=False),
        sa.Column("student_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("link_url", sa.String(length=700), nullable=True),
        sa.Column("github_url", sa.String(length=700), nullable=True),
        sa.Column("notes", sa.Text(), nullable=False),
        sa.Column("file_path", sa.String(length=700), nullable=True),
        sa.Column("original_filename", sa.String(length=255), nullable=True),
        sa.Column("status", submission_status_enum, nullable=False),
        sa.Column("feedback", sa.Text(), nullable=False),
        sa.Column("reviewed_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_submissions_id", "submissions", ["id"])
    op.create_index("ix_submissions_task_id", "submissions", ["task_id"])
    op.create_index("ix_submissions_student_id", "submissions", ["student_id"])
    op.create_index("ix_submissions_status", "submissions", ["status"])
    op.create_index("ix_submissions_submitted_at", "submissions", ["submitted_at"])
    op.create_index("ix_submissions_student_task_status", "submissions", ["student_id", "task_id", "status"])

    op.create_table(
        "points",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("submission_id", sa.Integer(), sa.ForeignKey("submissions.id"), nullable=True),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("reason", point_reason_enum, nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_points_id", "points", ["id"])
    op.create_index("ix_points_user_id", "points", ["user_id"])
    op.create_index("ix_points_submission_id", "points", ["submission_id"])
    op.create_index("ix_points_reason", "points", ["reason"])
    op.create_index("ix_points_created_at", "points", ["created_at"])
    op.create_index("ix_points_user_created_at", "points", ["user_id", "created_at"])
    op.create_index("ix_points_submission_reason", "points", ["submission_id", "reason"])

    op.create_table(
        "badges",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", badge_code_enum, nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("icon", sa.String(length=80), nullable=False),
    )
    op.create_index("ix_badges_id", "badges", ["id"])
    op.create_index("ix_badges_code", "badges", ["code"], unique=True)

    op.create_table(
        "user_badges",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("badge_id", sa.Integer(), sa.ForeignKey("badges.id"), nullable=False),
        sa.Column("awarded_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("awarded_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "badge_id", name="uq_user_badge"),
    )
    op.create_index("ix_user_badges_id", "user_badges", ["id"])
    op.create_index("ix_user_badges_user_id", "user_badges", ["user_id"])
    op.create_index("ix_user_badges_badge_id", "user_badges", ["badge_id"])

    op.create_table(
        "announcements",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=220), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("is_pinned", sa.Boolean(), nullable=False),
        sa.Column("scheduled_for", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_announcements_id", "announcements", ["id"])
    op.create_index("ix_announcements_scheduled_for", "announcements", ["scheduled_for"])

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("type", notification_type_enum, nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_notifications_id", "notifications", ["id"])
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])
    op.create_index("ix_notifications_type", "notifications", ["type"])
    op.create_index("ix_notifications_created_at", "notifications", ["created_at"])
    op.create_index("ix_notifications_user_read_created", "notifications", ["user_id", "read_at", "created_at"])

    op.create_table(
        "statistics",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("metric_date", sa.Date(), nullable=False),
        sa.Column("total_members", sa.Integer(), nullable=False),
        sa.Column("active_members", sa.Integer(), nullable=False),
        sa.Column("completed_tasks", sa.Integer(), nullable=False),
        sa.Column("submission_rate", sa.Float(), nullable=False),
        sa.Column("team_performance", sa.JSON(), nullable=False),
        sa.Column("top_members", sa.JSON(), nullable=False),
        sa.Column("weekly_activity", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_statistics_id", "statistics", ["id"])
    op.create_index("ix_statistics_metric_date", "statistics", ["metric_date"])


def downgrade() -> None:
    op.drop_index("ix_statistics_metric_date", table_name="statistics")
    op.drop_index("ix_statistics_id", table_name="statistics")
    op.drop_table("statistics")
    op.drop_index("ix_notifications_created_at", table_name="notifications")
    op.drop_index("ix_notifications_user_read_created", table_name="notifications")
    op.drop_index("ix_notifications_type", table_name="notifications")
    op.drop_index("ix_notifications_user_id", table_name="notifications")
    op.drop_index("ix_notifications_id", table_name="notifications")
    op.drop_table("notifications")
    op.drop_index("ix_announcements_scheduled_for", table_name="announcements")
    op.drop_index("ix_announcements_id", table_name="announcements")
    op.drop_table("announcements")
    op.drop_index("ix_user_badges_badge_id", table_name="user_badges")
    op.drop_index("ix_user_badges_user_id", table_name="user_badges")
    op.drop_index("ix_user_badges_id", table_name="user_badges")
    op.drop_table("user_badges")
    op.drop_index("ix_badges_code", table_name="badges")
    op.drop_index("ix_badges_id", table_name="badges")
    op.drop_table("badges")
    op.drop_index("ix_points_created_at", table_name="points")
    op.drop_index("ix_points_submission_reason", table_name="points")
    op.drop_index("ix_points_user_created_at", table_name="points")
    op.drop_index("ix_points_reason", table_name="points")
    op.drop_index("ix_points_submission_id", table_name="points")
    op.drop_index("ix_points_user_id", table_name="points")
    op.drop_index("ix_points_id", table_name="points")
    op.drop_table("points")
    op.drop_index("ix_submissions_submitted_at", table_name="submissions")
    op.drop_index("ix_submissions_student_task_status", table_name="submissions")
    op.drop_index("ix_submissions_status", table_name="submissions")
    op.drop_index("ix_submissions_student_id", table_name="submissions")
    op.drop_index("ix_submissions_task_id", table_name="submissions")
    op.drop_index("ix_submissions_id", table_name="submissions")
    op.drop_table("submissions")
    op.drop_index("ix_tasks_deadline", table_name="tasks")
    op.drop_index("ix_tasks_category", table_name="tasks")
    op.drop_index("ix_tasks_title", table_name="tasks")
    op.drop_index("ix_tasks_id", table_name="tasks")
    op.drop_table("tasks")
    op.drop_index("ix_users_team_id", table_name="users")
    op.drop_index("ix_users_role", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_id", table_name="users")
    op.drop_constraint("fk_teams_leader_id_users", "teams", type_="foreignkey")
    op.drop_table("users")
    op.drop_index("ix_teams_name", table_name="teams")
    op.drop_index("ix_teams_leader_id", table_name="teams")
    op.drop_index("ix_teams_id", table_name="teams")
    op.drop_table("teams")
    notification_type_enum.drop(op.get_bind(), checkfirst=True)
    badge_code_enum.drop(op.get_bind(), checkfirst=True)
    point_reason_enum.drop(op.get_bind(), checkfirst=True)
    submission_status_enum.drop(op.get_bind(), checkfirst=True)
    task_difficulty_enum.drop(op.get_bind(), checkfirst=True)
    task_category_enum.drop(op.get_bind(), checkfirst=True)
    role_enum.drop(op.get_bind(), checkfirst=True)
