from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session, require_permissions
from app.models.user import Permission
from app.schemas.treasury import (
    BankTreasurySnapshotResponse,
    UsdtWalletAssignRequest,
    UsdtWalletInventoryCreate,
    UsdtWalletInventoryResponse,
    UsdtWalletSweepRequest,
)
from app.services.bank_treasury import BankTreasuryService
from app.services.usdt_wallet_ops import UsdtWalletOpsService

router = APIRouter()


@router.get("/bank-snapshots", response_model=list[BankTreasurySnapshotResponse], dependencies=[Depends(require_permissions(Permission.settings_read))])
async def list_bank_snapshots(session: AsyncSession = Depends(get_session)) -> list[BankTreasurySnapshotResponse]:
    items = await BankTreasuryService(session).list_snapshots()
    return [BankTreasurySnapshotResponse.model_validate(item) for item in items]


@router.post("/bank-snapshots/sync", response_model=BankTreasurySnapshotResponse, dependencies=[Depends(require_permissions(Permission.settings_write))])
async def sync_bank_snapshot(session: AsyncSession = Depends(get_session)) -> BankTreasurySnapshotResponse:
    try:
        item = await BankTreasuryService(session).sync_sepay_balance()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return BankTreasurySnapshotResponse.model_validate(item)


@router.get("/usdt-wallets", response_model=list[UsdtWalletInventoryResponse], dependencies=[Depends(require_permissions(Permission.settings_read))])
async def list_usdt_wallets(session: AsyncSession = Depends(get_session)) -> list[UsdtWalletInventoryResponse]:
    items = await UsdtWalletOpsService(session).list_wallets()
    return [UsdtWalletInventoryResponse.model_validate(item) for item in items]


@router.post("/usdt-wallets", response_model=UsdtWalletInventoryResponse, dependencies=[Depends(require_permissions(Permission.settings_write))])
async def create_usdt_wallet(payload: UsdtWalletInventoryCreate, session: AsyncSession = Depends(get_session)) -> UsdtWalletInventoryResponse:
    try:
        item = await UsdtWalletOpsService(session).create_wallet(address=payload.address, label=payload.label, note=payload.note)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return UsdtWalletInventoryResponse.model_validate(item)


@router.post("/usdt-wallets/{wallet_id}/assign", response_model=UsdtWalletInventoryResponse, dependencies=[Depends(require_permissions(Permission.customer_write))])
async def assign_usdt_wallet(wallet_id: int, payload: UsdtWalletAssignRequest, session: AsyncSession = Depends(get_session)) -> UsdtWalletInventoryResponse:
    try:
        item = await UsdtWalletOpsService(session).assign_wallet(wallet_id=wallet_id, customer_id=payload.customer_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return UsdtWalletInventoryResponse.model_validate(item)


@router.post("/usdt-wallets/{wallet_id}/refresh", response_model=UsdtWalletInventoryResponse, dependencies=[Depends(require_permissions(Permission.settings_write))])
async def refresh_usdt_wallet(wallet_id: int, session: AsyncSession = Depends(get_session)) -> UsdtWalletInventoryResponse:
    try:
        item = await UsdtWalletOpsService(session).refresh_wallet(wallet_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return UsdtWalletInventoryResponse.model_validate(item)


@router.post("/usdt-wallets/{wallet_id}/queue-sweep", response_model=UsdtWalletInventoryResponse, dependencies=[Depends(require_permissions(Permission.settings_write))])
async def queue_usdt_wallet_sweep(wallet_id: int, payload: UsdtWalletSweepRequest, session: AsyncSession = Depends(get_session)) -> UsdtWalletInventoryResponse:
    try:
        item = await UsdtWalletOpsService(session).queue_sweep(wallet_id=wallet_id, note=payload.note)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return UsdtWalletInventoryResponse.model_validate(item)

