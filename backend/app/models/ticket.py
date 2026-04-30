from datetime import datetime
from enum import Enum

from sqlalchemy import JSON, DateTime, Enum as SqlEnum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.ad_account import Platform
from app.models.base import Base, TimestampMixin


class TicketType(str, Enum):
    open_account = "open_account"
    support = "support"


class TicketStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    done = "done"
    rejected = "rejected"


class TicketPriority(str, Enum):
    low = "low"
    normal = "normal"
    high = "high"
    urgent = "urgent"


class Ticket(TimestampMixin, Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), index=True)
    assigned_to: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    type: Mapped[TicketType] = mapped_column(SqlEnum(TicketType, name="ticket_type"))
    platform: Mapped[Platform] = mapped_column(SqlEnum(Platform, name="ticket_platform"))
    status: Mapped[TicketStatus] = mapped_column(SqlEnum(TicketStatus, name="ticket_status"), default=TicketStatus.pending)
    priority: Mapped[TicketPriority] = mapped_column(SqlEnum(TicketPriority, name="ticket_priority"), default=TicketPriority.normal)
    form_data: Mapped[dict] = mapped_column(JSON, default=dict)
    lark_ticket_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    customer = relationship("Customer", back_populates="tickets")
    assignee = relationship("User", back_populates="assigned_tickets")

    @property
    def assigned_user_name(self) -> str | None:
        return self.assignee.full_name if self.assignee else None
