from datetime import datetime

from pydantic import BaseModel, Field

from app.models.ad_account import Platform
from app.models.ticket import TicketPriority, TicketStatus, TicketType
from app.schemas.common import ORMBase


class TicketCreate(BaseModel):
    customer_id: int
    assigned_to: int | None = None
    type: TicketType
    platform: Platform
    priority: TicketPriority = TicketPriority.normal
    form_data: dict = Field(default_factory=dict)
    note: str | None = None


class TicketUpdate(BaseModel):
    assigned_to: int | None = None
    status: TicketStatus | None = None
    priority: TicketPriority | None = None
    note: str | None = None


class TicketResponse(ORMBase):
    id: int
    customer_id: int
    assigned_to: int | None = None
    assigned_user_name: str | None = None
    type: TicketType
    platform: Platform
    status: TicketStatus
    priority: TicketPriority
    form_data: dict
    lark_ticket_id: str | None = None
    note: str | None = None
    created_at: datetime
    updated_at: datetime
