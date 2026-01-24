"""Pydantic schemas for Role."""

from datetime import datetime

from app.schemas.common import BaseSchema
from app.schemas.permission import PermissionResponse


class RoleBase(BaseSchema):
    """Base schema for Role with common fields."""

    name: str
    description: str | None = None


class RoleCreate(RoleBase):
    """Schema for creating a new role."""

    pass


class RoleUpdate(BaseSchema):
    """Schema for updating a role."""

    name: str | None = None
    description: str | None = None


class RoleResponse(RoleBase):
    """Schema for role response without permissions."""

    id: int
    created_at: datetime
    updated_at: datetime


class RoleWithPermissionsResponse(RoleResponse):
    """Schema for role response including permissions."""

    permissions: list[PermissionResponse] = []