from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session, require_permissions
from app.models.user import Permission
from app.schemas.integrations import FacebookValidationResponse, IntegrationHealthResponse
from app.services.integrations import IntegrationHealthService

router = APIRouter()


@router.get("/health", response_model=list[IntegrationHealthResponse], dependencies=[Depends(require_permissions(Permission.integration_read))])
async def integrations_health(session: AsyncSession = Depends(get_session)) -> list[IntegrationHealthResponse]:
    return await IntegrationHealthService(session).check_all()


@router.get("/facebook/validate", response_model=FacebookValidationResponse, dependencies=[Depends(require_permissions(Permission.integration_read))])
async def validate_facebook_credentials(session: AsyncSession = Depends(get_session)) -> FacebookValidationResponse:
    return await IntegrationHealthService(session).validate_facebook_credentials()
