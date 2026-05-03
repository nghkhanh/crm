from decimal import Decimal
from typing import Any

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

    async def get_api_token(self) -> str:
        settings_map = await SettingsService(self.session).get_settings_map()
        return settings_map.get("sepay_api_token", "")

    @staticmethod
    def _pick(data: dict[str, Any], *keys: str) -> Any:
        for key in keys:
            value = data.get(key)
            if value not in (None, ""):
                return value
        return None

    @classmethod
    def parse_webhook_payload(cls, payload: dict[str, Any]) -> tuple[str, Decimal, str | None, str, dict[str, Any]]:
        data = payload.get("data") if isinstance(payload.get("data"), dict) else payload
        reference = cls._pick(data, "reference", "code", "content", "description", "transferContent")
        amount_raw = cls._pick(data, "amount", "transferAmount", "transfer_amount")
        note = cls._pick(data, "note", "description", "content", "transferContent")
        external_id = str(cls._pick(data, "id", "transaction_id", "transactionId") or "").strip()
        if not reference:
            raise ValueError("SePay webhook is missing reference/code/content")
        if amount_raw in (None, ""):
            raise ValueError("SePay webhook is missing amount/transferAmount")
        amount = Decimal(str(amount_raw))
        normalized_reference = str(reference).strip()
        normalized_external_id = external_id or WebhookEventService.fingerprint(
            normalized_reference,
            amount,
            str(note).strip() if note else None,
        )
        return (
            normalized_reference,
            amount,
            str(note).strip() if note else None,
            normalized_external_id,
            data,
        )

    async def process_webhook(self, reference: str, amount: Decimal, note: str | None = None) -> bool:
        external_id = WebhookEventService.fingerprint(reference, amount, note)
        return await self.process_webhook_event(
            reference=reference,
            amount=amount,
            note=note,
            external_id=external_id,
            raw_payload={"reference": reference, "amount": str(amount), "note": note},
        )

    async def process_webhook_event(
        self,
        *,
        reference: str,
        amount: Decimal,
        note: str | None,
        external_id: str,
        raw_payload: dict[str, Any],
    ) -> bool:
        event_service = WebhookEventService(self.session)
        if await event_service.already_processed("sepay", external_id):
            await ReconciliationService(self.session).create_record(
                channel=ReconciliationChannel.bank,
                status=ReconciliationStatus.duplicate,
                external_id=external_id,
                amount=amount,
                reference=reference,
                note=note,
                raw_payload=raw_payload,
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
                raw_payload=raw_payload,
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
            raw_payload=raw_payload,
        )
        await event_service.record(
            source="sepay",
            event_type="topup_bank",
            external_id=external_id,
            payload_json=raw_payload,
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
