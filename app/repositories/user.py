"""Repository for User model."""

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.role import Role
from app.models.user import User, UserStatus
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User CRUD operations with soft delete support."""

    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> User | None:
        """Get a user by email (excludes soft-deleted users)."""
        query = select(User).where(
            User.email == email,
            User.deleted_at.is_(None),
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_with_roles(self, user_id: int) -> User | None:
        """Get a user with roles loaded (excludes soft-deleted users)."""
        query = (
            select(User)
            .options(selectinload(User.roles))
            .where(User.id == user_id, User.deleted_at.is_(None))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_email_with_roles(self, email: str) -> User | None:
        """Get a user by email with roles loaded."""
        query = (
            select(User)
            .options(selectinload(User.roles))
            .where(User.email == email, User.deleted_at.is_(None))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_with_roles_and_permissions(self, user_id: int) -> User | None:
        """Get a user with roles and permissions loaded (excludes soft-deleted users)."""
        query = (
            select(User)
            .options(selectinload(User.roles).selectinload(Role.permissions))
            .where(User.id == user_id, User.deleted_at.is_(None))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_email_with_roles_and_permissions(self, email: str) -> User | None:
        """Get a user by email with roles and permissions loaded."""
        query = (
            select(User)
            .options(selectinload(User.roles).selectinload(Role.permissions))
            .where(User.email == email, User.deleted_at.is_(None))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
        **filters: Any,
    ) -> list[User]:
        """Get multiple users with optional pagination and filters."""
        query = select(User).filter_by(**filters).offset(skip).limit(limit)

        if not include_deleted:
            query = query.where(User.deleted_at.is_(None))

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_all_with_roles(
        self,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
        status: UserStatus | None = None,
    ) -> list[User]:
        """Get all users with their roles loaded."""
        query = select(User).options(selectinload(User.roles)).offset(skip).limit(limit)

        if not include_deleted:
            query = query.where(User.deleted_at.is_(None))

        if status is not None:
            # Use _status column (string) and compare with enum value
            query = query.where(User._status == status.value)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count(
        self,
        include_deleted: bool = False,
        **filters: Any,
    ) -> int:
        """Count users matching the filters."""
        query = select(func.count()).select_from(User).filter_by(**filters)

        if not include_deleted:
            query = query.where(User.deleted_at.is_(None))

        result = await self.session.execute(query)
        return result.scalar() or 0

    async def soft_delete(self, user_id: int) -> User | None:
        """Soft delete a user by setting deleted_at timestamp."""
        user = await self.get(user_id)
        if user is None or user.deleted_at is not None:
            return None

        user.deleted_at = datetime.now(timezone.utc)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def restore(self, user_id: int) -> User | None:
        """Restore a soft-deleted user."""
        query = select(User).where(User.id == user_id)
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()

        if user is None or user.deleted_at is None:
            return None

        user.deleted_at = None
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def add_role(self, user: User, role: Role) -> User:
        """Add a role to a user."""
        if role not in user.roles:
            user.roles.append(role)
            await self.session.flush()
        # Reload with roles to avoid lazy loading issues
        return await self.get_with_roles(user.id)  # type: ignore

    async def remove_role(self, user: User, role: Role) -> User:
        """Remove a role from a user."""
        if role in user.roles:
            user.roles.remove(role)
            await self.session.flush()
        # Reload with roles to avoid lazy loading issues
        return await self.get_with_roles(user.id)  # type: ignore

    async def verify_email(self, user: User) -> User:
        """Mark user's email as verified and activate account."""
        user.email_verified_at = datetime.now(timezone.utc)
        user.status = UserStatus.ACTIVE
        await self.session.flush()
        # Reload with roles to avoid lazy loading issues
        return await self.get_with_roles(user.id)  # type: ignore