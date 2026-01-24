"""Base repository with generic CRUD operations."""

from typing import Any, Generic, TypeVar

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Generic repository providing common CRUD operations.

    Usage:
        class UserRepository(BaseRepository[User]):
            def __init__(self, session: AsyncSession):
                super().__init__(User, session)
    """

    def __init__(self, model: type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get(self, id: Any) -> ModelType | None:
        """Get a single record by ID."""
        return await self.session.get(self.model, id)

    async def get_by(self, **kwargs: Any) -> ModelType | None:
        """Get a single record by arbitrary filters."""
        query = select(self.model).filter_by(**kwargs)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        **filters: Any,
    ) -> list[ModelType]:
        """Get multiple records with optional pagination and filters."""
        query = select(self.model).filter_by(**filters).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count(self, **filters: Any) -> int:
        """Count records matching the filters."""
        query = select(func.count()).select_from(self.model).filter_by(**filters)
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def create(self, **data: Any) -> ModelType:
        """Create a new record."""
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def update(self, id: Any, **data: Any) -> ModelType | None:
        """Update a record by ID."""
        instance = await self.get(id)
        if instance is None:
            return None

        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def update_where(self, filters: dict[str, Any], **data: Any) -> int:
        """Update multiple records matching filters. Returns count of updated rows."""
        query = update(self.model).filter_by(**filters).values(**data)
        result = await self.session.execute(query)
        return int(result.rowcount)  # type: ignore

    async def delete(self, id: Any) -> bool:
        """Delete a record by ID. Returns True if deleted."""
        instance = await self.get(id)
        if instance is None:
            return False

        await self.session.delete(instance)
        await self.session.flush()
        return True

    async def delete_where(self, **filters: Any) -> int:
        """Delete multiple records matching filters. Returns count of deleted rows."""
        query = delete(self.model).filter_by(**filters)
        result = await self.session.execute(query)
        return int(result.rowcount)  # type: ignore

    async def exists(self, **filters: Any) -> bool:
        """Check if a record exists matching the filters."""
        count = await self.count(**filters)
        return count > 0