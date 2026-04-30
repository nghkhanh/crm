from datetime import datetime

from app.schemas.common import ORMBase


class TicketTimelineEntry(ORMBase):
    id: int
    user_id: int | None = None
    user_name: str | None = None
    action: str
    metadata_json: dict
    created_at: datetime
