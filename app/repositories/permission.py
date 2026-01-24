"""Repository for Permission model."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.permission import Permission
from app.repositories.base import BaseRepository


class PermissionRepository(BaseRepository[Permission]):
    """Repository for Permission CRUD operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(Permission, session)

    async def get_by_code(self, code: str) -> Permission | None:
        """Get a permission by its code."""
        return await self.get_by(code=code)

    async def get_by_codes(self, codes: list[str]) -> list[Permission]:
        """Get multiple permissions by their codes."""
        from sqlalchemy import select

        query = select(Permission).where(Permission.code.in_(codes))
        result = await self.session.execute(query)
        return list(result.scalars().all())