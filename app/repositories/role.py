"""Repository for Role model."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.permission import Permission
from app.models.role import Role
from app.repositories.base import BaseRepository


class RoleRepository(BaseRepository[Role]):
    """Repository for Role CRUD operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(Role, session)

    async def get_by_name(self, name: str) -> Role | None:
        """Get a role by its name."""
        return await self.get_by(name=name)

    async def get_with_permissions(self, role_id: int) -> Role | None:
        """Get a role with its permissions loaded."""
        query = select(Role).options(selectinload(Role.permissions)).where(Role.id == role_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all_with_permissions(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Role]:
        """Get all roles with their permissions loaded."""
        query = select(Role).options(selectinload(Role.permissions)).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def add_permission(self, role: Role, permission: Permission) -> Role:
        """Add a permission to a role."""
        if permission not in role.permissions:
            role.permissions.append(permission)
            await self.session.flush()
            await self.session.refresh(role)
        return role

    async def remove_permission(self, role: Role, permission: Permission) -> Role:
        """Remove a permission from a role."""
        if permission in role.permissions:
            role.permissions.remove(permission)
            await self.session.flush()
            await self.session.refresh(role)
        return role