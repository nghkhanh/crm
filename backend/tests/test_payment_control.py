from decimal import Decimal

from app.models.ad_account import AdAccount, FacebookPaymentStatus
from app.services.smit_sync import SmitSyncService


def test_payment_control_marks_overdue_when_due_exceeds_prepaid():
    account = AdAccount(
        customer_id=1,
        platform="facebook",
        account_id="act_1",
        account_name="Account A",
        amount_due=Decimal("120"),
        prepaid_balance=Decimal("100"),
        payment_threshold=Decimal("20"),
    )

    assert SmitSyncService.resolve_payment_status(account) == FacebookPaymentStatus.overdue


def test_payment_control_marks_due_when_prepaid_hits_threshold():
    account = AdAccount(
        customer_id=1,
        platform="facebook",
        account_id="act_2",
        account_name="Account B",
        amount_due=Decimal("20"),
        prepaid_balance=Decimal("50"),
        payment_threshold=Decimal("50"),
    )

    assert SmitSyncService.resolve_payment_status(account) == FacebookPaymentStatus.due


def test_payment_control_marks_healthy_when_prepaid_is_safe():
    account = AdAccount(
        customer_id=1,
        platform="facebook",
        account_id="act_3",
        account_name="Account C",
        amount_due=Decimal("20"),
        prepaid_balance=Decimal("150"),
        payment_threshold=Decimal("50"),
    )

    assert SmitSyncService.resolve_payment_status(account) == FacebookPaymentStatus.healthy
