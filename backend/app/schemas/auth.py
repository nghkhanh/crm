from pydantic import BaseModel, Field

from app.models.user import UserRole, UserStatus
from app.schemas.common import ORMBase


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class AdminResetPasswordRequest(BaseModel):
    email: str
    new_password: str


class StaffCreateRequest(BaseModel):
    full_name: str
    email: str
    password: str = Field(min_length=8)
    role: UserRole = UserRole.sub_admin
    phone: str | None = None
    team_name: str | None = None
    status: UserStatus = UserStatus.enabled


class StaffUpdateRequest(BaseModel):
    full_name: str | None = None
    role: UserRole | None = None
    phone: str | None = None
    team_name: str | None = None
    status: UserStatus | None = None


class UserResponse(ORMBase):
    id: int
    email: str
    full_name: str
    role: UserRole
    phone: str | None = None
    team_name: str | None = None
    status: UserStatus
