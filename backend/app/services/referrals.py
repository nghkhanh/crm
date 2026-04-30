from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.referral import Referral
from app.models.transaction import Transaction, TransactionType


class ReferralService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def recalculate(self) -> dict[str, int]:
        result = await self.session.execute(select(Referral))
        referrals = result.scalars().all()
        updated = 0
        for referral in referrals:
            tx_result = await self.session.execute(
                select(Transaction).where(
                    Transaction.customer_id == referral.referee_id,
                    Transaction.type.in_([TransactionType.topup_bank, TransactionType.topup_usdt]),
                )
            )
            total_topup = sum((tx.amount for tx in tx_result.scalars().all()), Decimal("0.00"))
            referral.total_earned = (total_topup * referral.commission_rate) / Decimal("100.00")
            updated += 1
        await self.session.commit()
        return {"updated": updated}
