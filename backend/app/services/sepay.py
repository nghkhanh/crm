from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer
from app.models.payment_reconciliation import ReconciliationChannel, ReconciliationStatus
from app.models.transaction import Transaction, TransactionSource, TransactionStatus, TransactionType
from app.services.reconciliation import ReconciliationService
from app.services.audit import write_audit_log
from app.services.settings import SettingsService
from app.services.webhook_events import WebhookEventService


class SePayService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_webhook_secret(self) -> str:
        settings_map = await SettingsService(self.session).get_settings_map()
        return settings_map.get("sepay_webhook_secret", "")

    async def process_webhook(self, reference: str, amount: Decimal, note: str | None = None) -> bool:
        external_id = WebhookEventService.fingerprint(reference, amount, note)
        event_service = WebhookEventService(self.session)
        if await event_service.already_processed("sepay", external_id):
            await ReconciliationService(self.session).create_record(
                channel=ReconciliationChannel.bank,
                status=ReconciliationStatus.duplicate,
                external_id=external_id,
                amount=amount,
                reference=reference,
                note=note,
                raw_payload={"reference": reference, "amount": str(amount), "note": note},
            )
            await self.session.commit()
            return True

        result = await self.session.execute(select(Customer).where(Customer.referral_code == reference))
        customer = result.scalar_one_or_none()
        if not customer:
            await ReconciliationService(self.session).create_record(
                channel=ReconciliationChannel.bank,
                status=ReconciliationStatus.unmatched,
                external_id=external_id,
                amount=amount,
                reference=reference,
                note=note,
                raw_payload={"reference": reference, "amount": str(amount), "note": note},
            )
            await self.session.commit()
            return False

        balance_before = Decimal(customer.wallet_balance)
        customer.wallet_balance += amount
        transaction = Transaction(
            customer_id=customer.id,
            type=TransactionType.topup_bank,
            source=TransactionSource.sepay,
            status=TransactionStatus.posted,
            amount=amount,
            balance_before=balance_before,
            balance_after=Decimal(customer.wallet_balance),
            reference=reference,
            note=note or "Auto topup via SePay",
        )
        self.session.add(transaction)
        await self.session.flush()
        await ReconciliationService(self.session).create_record(
            channel=ReconciliationChannel.bank,
            status=ReconciliationStatus.credited,
            external_id=external_id,
            amount=amount,
            customer_id=customer.id,
            transaction_id=transaction.id,
            reference=reference,
            note=note,
            raw_payload={"reference": reference, "amount": str(amount), "note": note},
        )
        await event_service.record(
            source="sepay",
            event_type="topup_bank",
            external_id=external_id,
            payload_json={"reference": reference, "amount": str(amount), "note": note},
        )
        await write_audit_log(
            self.session,
            user_id=None,
            action="webhook.sepay_processed",
            entity_type="transaction",
            entity_id=transaction.id,
            metadata_json={"customer_id": customer.id, "reference": reference, "amount": str(amount)},
        )
        await self.session.commit()
        return True
