from datetime import datetime

from pydantic import BaseModel


class HealthComponent(BaseModel):
    name: str
    status: str
    detail: str


class HealthStatusResponse(BaseModel):
    status: str
    timestamp: datetime
    components: list[HealthComponent]
