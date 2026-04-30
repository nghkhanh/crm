"""webhook events

Revision ID: 20260426_0005
Revises: 20260426_0004
Create Date: 2026-04-26 23:25:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260426_0005"
down_revision = "20260426_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "webhook_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("source", "external_id", name="uq_webhook_events_source_external_id"),
    )
    op.create_index(op.f("ix_webhook_events_source"), "webhook_events", ["source"], unique=False)
    op.create_index(op.f("ix_webhook_events_event_type"), "webhook_events", ["event_type"], unique=False)
    op.create_index(op.f("ix_webhook_events_external_id"), "webhook_events", ["external_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_webhook_events_external_id"), table_name="webhook_events")
    op.drop_index(op.f("ix_webhook_events_event_type"), table_name="webhook_events")
    op.drop_index(op.f("ix_webhook_events_source"), table_name="webhook_events")
    op.drop_table("webhook_events")
