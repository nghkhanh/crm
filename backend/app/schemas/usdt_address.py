from datetime import datetime

from pydantic import BaseModel, field_validator

from app.models.customer_usdt_address import UsdtAddressNetwork, UsdtAddressStatus
from app.schemas.common import ORMBase


class CustomerUsdtAddressCreate(BaseModel):
    address: str
    label: str | None = None
    network: UsdtAddressNetwork = UsdtAddressNetwork.trc20

    @field_validator("address")
    @classmethod
    def validate_address(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized.startswith("T") or len(normalized) < 30:
            raise ValueError("USDT TRON deposit address is invalid")
        return normalized


class CustomerUsdtAddressUpdate(BaseModel):
    label: str | None = None
    status: UsdtAddressStatus | None = None


class CustomerUsdtAddressResponse(ORMBase):
    id: int
    customer_id: int
    network: UsdtAddressNetwork
    address: str
    label: str | None = None
    status: UsdtAddressStatus
    assigned_at: datetime
    last_seen_at: datetime | None = None
    created_at: datetime
