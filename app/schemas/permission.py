"""Pydantic schemas for Permission."""

from datetime import datetime

from app.schemas.common import BaseSchema


class PermissionBase(BaseSchema):
    """Base schema for Permission with common fields."""

    code: str
    description: str | None = None


class PermissionCreate(PermissionBase):
    """Schema for creating a new permission."""

    pass


class PermissionUpdate(BaseSchema):
    """Schema for updating a permission."""

    code: str | None = None
    description: str | None = None


class PermissionResponse(PermissionBase):
    """Schema for permission response."""

    id: int
    created_at: datetime
    updated_at: datetime