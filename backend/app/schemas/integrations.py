from pydantic import BaseModel


class IntegrationHealthResponse(BaseModel):
    name: str
    configured: bool
    reachable: bool
    message: str


class FacebookValidationResponse(BaseModel):
    valid: bool
    business_id: str
    business_name: str | None = None
    ad_accounts_count: int | None = None
    message: str
