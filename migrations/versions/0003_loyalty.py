"""loyalty: payments, bonuses

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-17

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # счётчики у клиента
    op.add_column("users", sa.Column("total_paid", sa.BigInteger(), server_default="0", nullable=False))
    op.add_column("users", sa.Column("bonus_balance", sa.BigInteger(), server_default="0", nullable=False))

    # настройки программы лояльности
    op.add_column("app_settings", sa.Column("bonus_threshold", sa.BigInteger(), server_default="20000000", nullable=False))
    op.add_column("app_settings", sa.Column("bonus_amount", sa.BigInteger(), server_default="1000000", nullable=False))

    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("amount", sa.BigInteger(), nullable=False),
        sa.Column("request_id", sa.Integer(), nullable=True),
        sa.Column("comment", sa.String(length=512), nullable=True),
        sa.Column("admin_id", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.telegram_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["request_id"], ["service_requests.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_payments_user_id", "payments", ["user_id"])

    op.create_table(
        "bonus_tx",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("amount", sa.BigInteger(), nullable=False),
        sa.Column("kind", sa.String(length=8), nullable=False),
        sa.Column("reason", sa.String(length=255), nullable=True),
        sa.Column("admin_id", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.telegram_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_bonus_tx_user_id", "bonus_tx", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_bonus_tx_user_id", table_name="bonus_tx")
    op.drop_table("bonus_tx")
    op.drop_index("ix_payments_user_id", table_name="payments")
    op.drop_table("payments")
    op.drop_column("app_settings", "bonus_amount")
    op.drop_column("app_settings", "bonus_threshold")
    op.drop_column("users", "bonus_balance")
    op.drop_column("users", "total_paid")
