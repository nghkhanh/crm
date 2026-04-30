from datetime import datetime

from app.schemas.common import ORMBase


class AuditLogResponse(ORMBase):
    id: int
    user_id: int | None = None
    action: str
    entity_type: str
    entity_id: str
    metadata_json: dict
    created_at: datetime

