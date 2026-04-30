from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session, require_permissions
from app.models.user import Permission
from app.schemas.dashboard import DashboardSummary
from app.services.dashboard import DashboardService

router = APIRouter()


@router.get("/summary", response_model=DashboardSummary, dependencies=[Depends(require_permissions(Permission.dashboard_read))])
async def get_summary(session: AsyncSession = Depends(get_session)) -> DashboardSummary:
    return await DashboardService(session).get_summary()
