"""Permission model for granular access control."""

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.role import Role


class Permission(Base, TimestampMixin):
    """
    Permission model representing a specific action that can be performed.

    Permissions are assigned to roles, and users inherit permissions through
    their assigned roles.

    Example codes: 'users.create', 'users.read', 'products.delete'
    """

    __tablename__ = "permission"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationships
    roles: Mapped[list["Role"]] = relationship(  # noqa: F821
        "Role",
        secondary="role_permission",
        back_populates="permissions",
    )

    def __repr__(self) -> str:
        return f"<Permission(id={self.id}, code='{self.code}')>"