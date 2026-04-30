from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


async def write_audit_log(
    session: AsyncSession,
    *,
    user_id: int | None,
    action: str,
    entity_type: str,
    entity_id: str | int,
    metadata_json: dict | None = None,
) -> None:
    session.add(
        AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=str(entity_id),
            metadata_json=metadata_json or {},
        )
    )
