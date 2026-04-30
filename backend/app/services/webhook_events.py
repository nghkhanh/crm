import hashlib

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.webhook_event import WebhookEvent


class WebhookEventService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def already_processed(self, source: str, external_id: str) -> bool:
        result = await self.session.execute(
            select(WebhookEvent.id).where(WebhookEvent.source == source, WebhookEvent.external_id == external_id)
        )
        return result.scalar_one_or_none() is not None

    async def record(self, *, source: str, event_type: str, external_id: str, payload_json: dict) -> None:
        self.session.add(
            WebhookEvent(
                source=source,
                event_type=event_type,
                external_id=external_id,
                payload_json=payload_json,
            )
        )

    @staticmethod
    def fingerprint(*parts: object) -> str:
        normalized = "|".join(str(part or "").strip() for part in parts)
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
