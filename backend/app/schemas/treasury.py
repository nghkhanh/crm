from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, field_validator

from app.schemas.common import ORMBase


class BankTreasurySnapshotResponse(ORMBase):
    id: int
    provider: str
    bank_account_id: str
    account_number: str | None = None
    account_name: str | None = None
    currency: str
    balance: Decimal
    available_balance: Decimal | None = None
    status_message: str | None = None
    synced_at: datetime
    created_at: datetime


class UsdtWalletInventoryCreate(BaseModel):
    address: str
    label: str | None = None
    note: str | None = None

    @field_validator("address", mode="before")
    @classmethod
    def validate_address(cls, value: str) -> str:
        normalized = str(value or "").strip()
        if len(normalized) != 34 or not normalized.startswith("T"):
            raise ValueError("Wallet address must be a valid TRON address")
        return normalized

    @field_validator("label", "note", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        normalized = str(value or "").strip()
        return normalized or None


class UsdtWalletInventoryUpdate(BaseModel):
    label: str | None = None
    note: str | None = None
    status: str | None = None
    sweep_status: str | None = None
    last_sweep_tx_id: str | None = None

    @field_validator("label", "note", "status", "sweep_status", "last_sweep_tx_id", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = str(value).strip()
        return normalized or None


class UsdtWalletAssignRequest(BaseModel):
    customer_id: int


class UsdtWalletSweepRequest(BaseModel):
    note: str | None = None

    @field_validator("note", mode="before")
    @classmethod
    def normalize_note(cls, value: str | None) -> str | None:
        normalized = str(value or "").strip()
        return normalized or None


class UsdtWalletInventoryResponse(ORMBase):
    id: int
    network: str
    address: str
    label: str | None = None
    status: str
    customer_id: int | None = None
    customer_usdt_address_id: int | None = None
    trx_balance: Decimal
    usdt_balance: Decimal
    gas_status: str
    sweep_status: str
    sweep_destination: str | None = None
    last_sweep_tx_id: str | None = None
    assigned_at: datetime | None = None
    last_balance_synced_at: datetime | None = None
    requested_sweep_at: datetime | None = None
    last_sweep_at: datetime | None = None
    note: str | None = None
    created_at: datetime

