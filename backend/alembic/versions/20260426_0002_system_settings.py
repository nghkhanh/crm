"""system settings

Revision ID: 20260426_0002
Revises: 20260426_0001
Create Date: 2026-04-26 00:30:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260426_0002"
down_revision = "20260426_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "system_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("key", sa.String(length=100), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(op.f("ix_system_settings_key"), "system_settings", ["key"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_system_settings_key"), table_name="system_settings")
    op.drop_table("system_settings")
