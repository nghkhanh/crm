from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment_reconciliation import PaymentReconciliation, ReconciliationChannel, ReconciliationStatus


class ReconciliationService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_record(
        self,
        *,
        channel: ReconciliationChannel,
        status: ReconciliationStatus,
        external_id: str,
        amount: Decimal,
        customer_id: int | None = None,
        transaction_id: int | None = None,
        reference: str | None = None,
        wallet_address: str | None = None,
        note: str | None = None,
        raw_payload: dict | None = None,
    ) -> PaymentReconciliation:
        record = PaymentReconciliation(
            channel=channel,
            status=status,
            external_id=external_id,
            amount=amount,
            customer_id=customer_id,
            transaction_id=transaction_id,
            reference=reference,
            wallet_address=wallet_address,
            note=note,
            raw_payload=raw_payload or {},
        )
        self.session.add(record)
        await self.session.flush()
        return record
