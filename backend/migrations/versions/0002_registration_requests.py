"""registration requests and team codes

Revision ID: 0002_registration_requests
Revises: 0001_initial
Create Date: 2026-06-27
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_registration_requests"
down_revision = "0001_initial"
branch_labels = None
depends_on = None

registration_status_enum = sa.Enum(
    "PENDING",
    "ACCEPTED",
    "REJECTED",
    "CHANGES_REQUESTED",
    name="registrationrequeststatus",
)


def upgrade() -> None:
    with op.batch_alter_table("teams") as batch_op:
        batch_op.add_column(sa.Column("team_code", sa.String(length=24), nullable=True))
        batch_op.add_column(sa.Column("is_code_active", sa.Boolean(), nullable=False, server_default=sa.true()))

    op.create_index("ix_teams_team_code", "teams", ["team_code"], unique=True)

    op.create_table(
        "registration_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("full_name", sa.String(length=180), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("bio", sa.Text(), nullable=False, server_default=""),
        sa.Column("team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("status", registration_status_enum, nullable=False),
        sa.Column("admin_note", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
    )
    op.create_index("ix_registration_requests_id", "registration_requests", ["id"])
    op.create_index("ix_registration_requests_email", "registration_requests", ["email"])
    op.create_index("ix_registration_requests_status", "registration_requests", ["status"])
    op.create_index("ix_registration_requests_team_id", "registration_requests", ["team_id"])
    op.create_index("ix_registration_requests_created_at", "registration_requests", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_registration_requests_created_at", table_name="registration_requests")
    op.drop_index("ix_registration_requests_team_id", table_name="registration_requests")
    op.drop_index("ix_registration_requests_status", table_name="registration_requests")
    op.drop_index("ix_registration_requests_email", table_name="registration_requests")
    op.drop_index("ix_registration_requests_id", table_name="registration_requests")
    op.drop_table("registration_requests")
    registration_status_enum.drop(op.get_bind(), checkfirst=True)

    op.drop_index("ix_teams_team_code", table_name="teams")
    with op.batch_alter_table("teams") as batch_op:
        batch_op.drop_column("is_code_active")
        batch_op.drop_column("team_code")
