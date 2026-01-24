"""Role model with permission associations."""

from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.permission import Permission
    from app.models.user import User

# Association table for Role-Permission many-to-many relationship
role_permission = Table(
    "role_permission",
    Base.metadata,
    Column("role_id", ForeignKey("role.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", ForeignKey("permission.id", ondelete="CASCADE"), primary_key=True),
)


class Role(Base, TimestampMixin):
    """
    Role model representing a set of permissions.

    Users can have multiple roles, and each role can have multiple permissions.

    Default roles: admin, seller, merchant, manufacturer
    """

    __tablename__ = "role"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationships
    permissions: Mapped[list["Permission"]] = relationship(  # noqa: F821
        "Permission",
        secondary=role_permission,
        back_populates="roles",
    )
    users: Mapped[list["User"]] = relationship(  # noqa: F821
        "User",
        secondary="user_role",
        back_populates="roles",
    )

    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name='{self.name}')>"

    def has_permission(self, permission_code: str) -> bool:
        """Check if this role has a specific permission."""
        return any(p.code == permission_code for p in self.permissions)