"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-07-08

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("lang", sa.String(length=2), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("telegram_id"),
    )

    op.create_table(
        "equipment",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("kind", sa.String(length=64), nullable=False),
        sa.Column("model", sa.String(length=128), nullable=True),
        sa.Column("install_date", sa.Date(), nullable=False),
        sa.Column("period_months", sa.Integer(), nullable=False),
        sa.Column("last_service_date", sa.Date(), nullable=True),
        sa.Column("next_service_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.telegram_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_equipment_next_service_date", "equipment", ["next_service_date"])

    op.create_table(
        "reminder_log",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("equipment_id", sa.Integer(), nullable=False),
        sa.Column("stage", sa.String(length=8), nullable=False),
        sa.Column("sent_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["equipment_id"], ["equipment.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_reminder_log_equipment_id", "reminder_log", ["equipment_id"])

    op.create_table(
        "service_requests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("equipment_id", sa.Integer(), nullable=True),
        sa.Column("type", sa.String(length=16), nullable=False),
        sa.Column("status", sa.String(length=8), nullable=False),
        sa.Column("comment", sa.String(length=512), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.telegram_id"]),
        sa.ForeignKeyConstraint(["equipment_id"], ["equipment.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "app_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("reminder_hour", sa.Integer(), nullable=False),
        sa.Column("reminder_minute", sa.Integer(), nullable=False),
        sa.Column("reminder_stages", sa.String(length=64), nullable=False),
        sa.Column("contacts", sa.String(length=1024), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "admins",
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("added_by", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("telegram_id"),
    )

    op.create_table(
        "broadcasts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("admin_id", sa.BigInteger(), nullable=False),
        sa.Column("segment", sa.String(length=64), nullable=False),
        sa.Column("sent_count", sa.Integer(), nullable=False),
        sa.Column("failed_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("broadcasts")
    op.drop_table("admins")
    op.drop_table("app_settings")
    op.drop_table("service_requests")
    op.drop_index("ix_reminder_log_equipment_id", table_name="reminder_log")
    op.drop_table("reminder_log")
    op.drop_index("ix_equipment_next_service_date", table_name="equipment")
    op.drop_table("equipment")
    op.drop_table("users")
