from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session, require_permissions
from app.models.ad_account import AdAccount, AdAccountStatus, Platform
from app.models.user import Permission
from app.schemas.ad_account import AdAccountCreate, AdAccountResponse, AdAccountUpdate
from app.services.fb_sync import FacebookSyncService

router = APIRouter()


@router.get("", response_model=list[AdAccountResponse], dependencies=[Depends(require_permissions(Permission.ad_account_read))])
async def list_ad_accounts(
    customer_id: int | None = None,
    status: AdAccountStatus | None = None,
    platform: Platform | None = None,
    session: AsyncSession = Depends(get_session),
) -> list[AdAccountResponse]:
    query = select(AdAccount)
    if customer_id:
        query = query.where(AdAccount.customer_id == customer_id)
    if status:
        query = query.where(AdAccount.status == status)
    if platform:
        query = query.where(AdAccount.platform == platform)
    result = await session.execute(query.order_by(AdAccount.created_at.desc()))
    return [AdAccountResponse.model_validate(item) for item in result.scalars().all()]


@router.post("", response_model=AdAccountResponse, dependencies=[Depends(require_permissions(Permission.ad_account_write))])
async def create_ad_account(payload: AdAccountCreate, session: AsyncSession = Depends(get_session)) -> AdAccountResponse:
    item = AdAccount(**payload.model_dump())
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return AdAccountResponse.model_validate(item)


@router.post("/sync", response_model=dict, dependencies=[Depends(require_permissions(Permission.ad_account_sync))])
async def sync_ad_accounts(session: AsyncSession = Depends(get_session)):
    return await FacebookSyncService(session).sync_accounts()


@router.get("/{account_id}", response_model=AdAccountResponse, dependencies=[Depends(require_permissions(Permission.ad_account_read))])
async def get_ad_account(account_id: int, session: AsyncSession = Depends(get_session)) -> AdAccountResponse:
    item = await session.get(AdAccount, account_id)
    if not item:
        raise HTTPException(status_code=404, detail="Ad account not found")
    return AdAccountResponse.model_validate(item)


@router.patch("/{account_id}", response_model=AdAccountResponse, dependencies=[Depends(require_permissions(Permission.ad_account_write))])
async def update_ad_account(account_id: int, payload: AdAccountUpdate, session: AsyncSession = Depends(get_session)) -> AdAccountResponse:
    item = await session.get(AdAccount, account_id)
    if not item:
        raise HTTPException(status_code=404, detail="Ad account not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    await session.commit()
    await session.refresh(item)
    return AdAccountResponse.model_validate(item)
