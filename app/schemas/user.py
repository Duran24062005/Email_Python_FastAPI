"""Pydantic schemas for User."""

from datetime import datetime

from pydantic import EmailStr, Field

from app.models.user import UserStatus
from app.schemas.common import BaseSchema
from app.schemas.role import RoleResponse


class UserBase(BaseSchema):
    """Base schema for User with common fields."""

    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: str | None = Field(None, max_length=20)
    address: str | None = None


class UserCreate(UserBase):
    """Schema for user registration."""

    password: str = Field(..., min_length=8, max_length=128)


class UserUpdate(BaseSchema):
    """Schema for updating user profile."""

    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    phone: str | None = Field(None, max_length=20)
    address: str | None = None


class UserResponse(UserBase):
    """Schema for user response (excludes sensitive data)."""

    id: int
    status: UserStatus
    email_verified_at: datetime | None
    created_at: datetime
    updated_at: datetime


class UserWithRolesResponse(UserResponse):
    """Schema for user response including roles."""

    roles: list[RoleResponse] = []


class UserAdminResponse(UserWithRolesResponse):
    """Schema for admin user response (includes deleted_at)."""

    deleted_at: datetime | None


# Auth-related schemas
class EmailVerificationRequest(BaseSchema):
    """Schema for email verification request."""

    token: str


class AssignRoleRequest(BaseSchema):
    """Schema for assigning a role to a user."""

    role_id: int