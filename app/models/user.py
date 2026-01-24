"""User model with role associations and soft delete support."""

import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, String, Table, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.role import Role
    from app.models.team import Team
    from app.models.email_model import Email


class UserStatus(str, enum.Enum):
    """User account status enum."""

    PENDING_VERIFICATION = "pending_verification"
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


# Association table for User-Role many-to-many relationship
user_role = Table(
    "user_role",
    Base.metadata,
    Column("user_id", ForeignKey("user.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", ForeignKey("role.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "assigned_at",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    ),
)


class User(Base, TimestampMixin):
    """
    User model representing a person with access to MUBE.

    Features:
    - Email/password authentication
    - Multiple roles (N:M relationship)
    - Soft delete support
    - Email verification flow
    """

    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    _status: Mapped[str] = mapped_column(
        "status",
        String(30),
        nullable=False,
        default=UserStatus.PENDING_VERIFICATION.value,
    )

    @property
    def status(self) -> UserStatus:
        """Get status as enum."""
        return UserStatus(self._status)

    @status.setter
    def status(self, value: UserStatus) -> None:
        """Set status from enum."""
        self._status = value.value if isinstance(value, UserStatus) else value

    email_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary=user_role,
        back_populates="users",
    )
    teams: Mapped[list["Team"]] = relationship(
        "Team",
        secondary="user_team",
        back_populates="members",
    )
    owned_teams: Mapped[list["Team"]] = relationship(
        "Team",
        foreign_keys="Team.owner_id",
        back_populates="owner",
    )
    emails: Mapped[list["Email"]] = relationship(
        "Email",
        back_populates="user",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}')>"

    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"

    @property
    def is_active(self) -> bool:
        """Check if user account is active."""
        return self.status == UserStatus.ACTIVE and self.deleted_at is None

    @property
    def is_deleted(self) -> bool:
        """Check if user has been soft deleted."""
        return self.deleted_at is not None

    def has_role(self, role_name: str) -> bool:
        """Check if user has a specific role."""
        return any(r.name == role_name for r in self.roles)

    def has_permission(self, permission_code: str) -> bool:
        """Check if user has a specific permission through any of their roles."""
        return any(role.has_permission(permission_code) for role in self.roles)

    def get_all_permissions(self) -> set[str]:
        """Get all permission codes for this user across all roles."""
        permissions = set()
        for role in self.roles:
            for permission in role.permissions:
                permissions.add(permission.code)
        return permissions

    def has_team(self, team_id: int) -> bool:
        """Check if user belongs to a specific team."""
        return any(team.id == team_id for team in self.teams)

    def is_team_owner(self, team_id: int) -> bool:
        """Check if user is the owner of a specific team."""
        return any(team.id == team_id for team in self.owned_teams)

    def get_teams(self) -> list["Team"]:
        """Get all teams the user belongs to."""
        return list(self.teams)