from sqlalchemy import JSON, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class WebhookEvent(TimestampMixin, Base):
    __tablename__ = "webhook_events"
    __table_args__ = (UniqueConstraint("source", "external_id", name="uq_webhook_events_source_external_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(50), index=True)
    event_type: Mapped[str] = mapped_column(String(100), index=True)
    external_id: Mapped[str] = mapped_column(String(255), index=True)
    payload_json: Mapped[dict] = mapped_column(JSON, default=dict)
