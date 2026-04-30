from decimal import Decimal

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_session, require_permissions
from app.models.customer import Customer
from app.models.payment_reconciliation import PaymentReconciliation, ReconciliationChannel, ReconciliationStatus
from app.models.transaction import Transaction, TransactionSource, TransactionStatus, TransactionType
from app.schemas.reconciliation import ReconciliationResponse
from app.models.user import Permission, User
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.services.audit import write_audit_log

router = APIRouter()


@router.get("", response_model=list[TransactionResponse], dependencies=[Depends(require_permissions(Permission.transaction_read))])
async def list_transactions(
    customer_id: int | None = None,
    type: TransactionType | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    session: AsyncSession = Depends(get_session),
) -> list[TransactionResponse]:
    query = select(Transaction)
    if customer_id:
        query = query.where(Transaction.customer_id == customer_id)
    if type:
        query = query.where(Transaction.type == type)
    if date_from:
        query = query.where(Transaction.created_at >= date_from)
    if date_to:
        query = query.where(Transaction.created_at <= date_to)
    result = await session.execute(query.order_by(Transaction.created_at.desc()))
    return [TransactionResponse.model_validate(item) for item in result.scalars().all()]


@router.post("", response_model=TransactionResponse, dependencies=[Depends(require_permissions(Permission.transaction_write))])
async def create_transaction(
    payload: TransactionCreate,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> TransactionResponse:
    customer = await session.get(Customer, payload.customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    delta = Decimal("0.00")
    if payload.type in {TransactionType.topup_bank, TransactionType.topup_usdt, TransactionType.adjustment}:
        delta = payload.amount
    elif payload.type in {TransactionType.fee, TransactionType.commission}:
        delta = -payload.amount

    projected_balance = Decimal(customer.wallet_balance) + delta
    if projected_balance < 0:
        raise HTTPException(status_code=400, detail="Transaction would make wallet balance negative")

    item = Transaction(
        **payload.model_dump(),
        created_by=user.id,
        source=TransactionSource.manual,
        status=TransactionStatus.posted,
        balance_before=Decimal(customer.wallet_balance),
        balance_after=projected_balance,
    )
    session.add(item)
    await session.flush()
    customer.wallet_balance = projected_balance
    await write_audit_log(
        session,
        user_id=user.id,
        action="transaction.create",
        entity_type="transaction",
        entity_id=item.id,
        metadata_json={
            "customer_id": customer.id,
            "type": item.type.value,
            "source": item.source.value,
            "status": item.status.value,
            "amount": str(item.amount),
            "balance_before": str(item.balance_before),
            "balance_after": str(item.balance_after),
        },
    )
    await session.commit()
    await session.refresh(item)
    return TransactionResponse.model_validate(item)


@router.get("/reconciliations/list", response_model=list[ReconciliationResponse], dependencies=[Depends(require_permissions(Permission.transaction_read))])
async def list_reconciliations(
    customer_id: int | None = None,
    channel: ReconciliationChannel | None = None,
    status: ReconciliationStatus | None = None,
    session: AsyncSession = Depends(get_session),
) -> list[ReconciliationResponse]:
    query = select(PaymentReconciliation)
    if customer_id:
        query = query.where(PaymentReconciliation.customer_id == customer_id)
    if channel:
        query = query.where(PaymentReconciliation.channel == channel)
    if status:
        query = query.where(PaymentReconciliation.status == status)
    result = await session.execute(query.order_by(PaymentReconciliation.created_at.desc()))
    return [ReconciliationResponse.model_validate(item) for item in result.scalars().all()]


@router.get("/{transaction_id}", response_model=TransactionResponse, dependencies=[Depends(require_permissions(Permission.transaction_read))])
async def get_transaction(transaction_id: int, session: AsyncSession = Depends(get_session)) -> TransactionResponse:
    item = await session.get(Transaction, transaction_id)
    if not item:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return TransactionResponse.model_validate(item)
