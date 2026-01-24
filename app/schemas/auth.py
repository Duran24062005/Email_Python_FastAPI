"""Pydantic schemas for authentication."""

from pydantic import EmailStr, Field

from app.schemas.common import BaseSchema
from app.schemas.user import UserWithRolesResponse


class LoginRequest(BaseSchema):
    """Schema for login request."""

    email: EmailStr
    password: str = Field(..., min_length=1)


class TokenResponse(BaseSchema):
    """Schema for token response after login."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: UserWithRolesResponse


class RefreshTokenRequest(BaseSchema):
    """Schema for refresh token request."""

    refresh_token: str


class RefreshTokenResponse(BaseSchema):
    """Schema for refresh token response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class VerifyTokenRequest(BaseSchema):
    """Schema for verify token request."""

    token: str


class VerifyTokenResponse(BaseSchema):
    """Schema for verify token response."""

    valid: bool
    user: UserWithRolesResponse | None = None