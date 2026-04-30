from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Agency CRM"
    database_url: str = Field(alias="DATABASE_URL")
    redis_url: str = Field(default="redis://redis:6379/0", alias="REDIS_URL")
    jwt_secret: str = Field(alias="JWT_SECRET")
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = Field(default=30, alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    jwt_refresh_token_expire_days: int = Field(default=7, alias="JWT_REFRESH_TOKEN_EXPIRE_DAYS")
    auth_lockout_max_attempts: int = Field(default=5, alias="AUTH_LOCKOUT_MAX_ATTEMPTS")
    auth_lockout_minutes: int = Field(default=15, alias="AUTH_LOCKOUT_MINUTES")
    auth_login_rate_limit_per_minute: int = Field(default=10, alias="AUTH_LOGIN_RATE_LIMIT_PER_MINUTE")
    auth_refresh_rate_limit_per_minute: int = Field(default=30, alias="AUTH_REFRESH_RATE_LIMIT_PER_MINUTE")
    webhook_rate_limit_per_minute: int = Field(default=120, alias="WEBHOOK_RATE_LIMIT_PER_MINUTE")
    fb_system_user_token: str = Field(default="", alias="FB_SYSTEM_USER_TOKEN")
    fb_business_id: str = Field(default="", alias="FB_BUSINESS_ID")
    sepay_webhook_secret: str = Field(default="", alias="SEPAY_WEBHOOK_SECRET")
    trongrid_api_key: str = Field(default="", alias="TRONGRID_API_KEY")
    agency_usdt_wallet: str = Field(default="", alias="AGENCY_USDT_WALLET")
    lark_webhook_url: str = Field(default="", alias="LARK_WEBHOOK_URL")
    backend_public_base_url: str = Field(default="http://localhost:8000", alias="BACKEND_PUBLIC_BASE_URL")
    frontend_public_base_url: str = Field(default="http://localhost:3000", alias="FRONTEND_PUBLIC_BASE_URL")
    default_admin_email: str = Field(default="admin@agency.local", alias="DEFAULT_ADMIN_EMAIL")
    default_admin_password: str = Field(default="changeme123", alias="DEFAULT_ADMIN_PASSWORD")
    default_commission_rate: float = Field(default=5, alias="DEFAULT_COMMISSION_RATE")
    seed_demo_data: bool = Field(default=False, alias="SEED_DEMO_DATA")
    cors_origins: list[str] = ["http://localhost:3000", "http://frontend:3000"]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
