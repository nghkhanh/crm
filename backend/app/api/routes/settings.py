from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session, require_permissions
from app.models.user import Permission
from app.schemas.settings import SystemSettingResponse, SystemSettingsUpdate
from app.services.audit import write_audit_log
from app.services.settings import SettingsService
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("", response_model=list[SystemSettingResponse], dependencies=[Depends(require_permissions(Permission.settings_read))])
async def list_settings(session: AsyncSession = Depends(get_session)) -> list[SystemSettingResponse]:
    items = await SettingsService(session).list_settings()
    return [SystemSettingResponse.model_validate(item) for item in items]


@router.patch("", response_model=list[SystemSettingResponse], dependencies=[Depends(require_permissions(Permission.settings_write))])
async def update_settings(
    payload: SystemSettingsUpdate,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> list[SystemSettingResponse]:
    items = await SettingsService(session).update_settings(payload)
    await write_audit_log(
        session,
        user_id=user.id,
        action="settings.update",
        entity_type="system_settings",
        entity_id="global",
        metadata_json={"keys": list(payload.model_dump().keys())},
    )
    await session.commit()
    return [SystemSettingResponse.model_validate(item) for item in items]
