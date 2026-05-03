import pytest

from app.schemas.health import HealthComponent
from app.schemas.settings import SystemSettingsUpdate
from app.services.health import HealthService


def test_settings_update_validates_and_normalizes_fields():
    payload = SystemSettingsUpdate(
        lark_webhook_url=" https://example.com/webhook ",
        fb_business_id="123456",
        agency_usdt_wallet="T123456789012345678901234567890123",
        usdt_trc20_contract=" TXLAQ63Xg1NAzckPwKHvzw7CSEmLMEqcdj ",
        sepay_bank_account_id="19",
        smit_base_url=" https://smit.example.com/ ",
        smit_sync_url_template="/api/accounts/{account_id}",
        default_commission_rate="12.50",
    )

    assert payload.lark_webhook_url == "https://example.com/webhook"
    assert payload.fb_business_id == "123456"
    assert payload.usdt_trc20_contract == "TXLAQ63Xg1NAzckPwKHvzw7CSEmLMEqcdj"
    assert payload.sepay_bank_account_id == "19"
    assert payload.smit_base_url == "https://smit.example.com"
    assert payload.default_commission_rate == "12.5"


def test_settings_update_rejects_invalid_values():
    with pytest.raises(ValueError):
        SystemSettingsUpdate(default_commission_rate="150")

    with pytest.raises(ValueError):
        SystemSettingsUpdate(lark_webhook_url="not-a-url")

    with pytest.raises(ValueError):
        SystemSettingsUpdate(agency_usdt_wallet="invalid-wallet")

    with pytest.raises(ValueError):
        SystemSettingsUpdate(sepay_bank_account_id="bank-01")

    with pytest.raises(ValueError):
        SystemSettingsUpdate(smit_sync_url_template="accounts/no-placeholder")


@pytest.mark.asyncio
async def test_readiness_degraded_when_dependency_fails(monkeypatch):
    async def ok_database(self):
        return HealthComponent(name="database", status="ok", detail="Database connection successful")

    async def failing_redis(self):
        return HealthComponent(name="redis", status="error", detail="Redis unavailable")

    def ok_scheduler(self):
        return HealthComponent(name="scheduler", status="ok", detail="Scheduler is running")

    monkeypatch.setattr(HealthService, "_check_database", ok_database)
    monkeypatch.setattr(HealthService, "_check_redis", failing_redis)
    monkeypatch.setattr(HealthService, "_check_scheduler", ok_scheduler)

    payload = await HealthService().check_readiness()

    assert payload.status == "degraded"
    assert any(component.name == "redis" and component.status == "error" for component in payload.components)
