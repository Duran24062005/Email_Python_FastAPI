"""Team model for organizing users into teams."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, String, Text, DateTime, Table, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


# Association table for User-Team many-to-many relationship
user_team = Table(
    "user_team",
    Base.metadata,
    Column("user_id", ForeignKey("user.id", ondelete="CASCADE"), primary_key=True),
    Column("team_id", ForeignKey("team.id", ondelete="CASCADE"), primary_key=True),
    Column("role_in_team", String(50), nullable=False, default="member"),  # owner, member
    Column(
        "joined_at",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    ),
)


class Team(Base, TimestampMixin):
    """
    Team model representing a group of users.
    
    Teams allow users to organize and collaborate. Each team has:
    - An owner (the user who created it)
    - Members (users who belong to the team)
    - Roles within the team (owner, member - extensible for future roles)
    """

    __tablename__ = "team"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    owner: Mapped["User"] = relationship(
        "User",
        foreign_keys=[owner_id],
        back_populates="owned_teams"
    )
    members: Mapped[list["User"]] = relationship(
        "User",
        secondary=user_team,
        back_populates="teams",
    )

    def __repr__(self) -> str:
        return f"<Team(id={self.id}, name='{self.name}')>"

    @property
    def is_deleted(self) -> bool:
        """Check if team has been soft deleted."""
        return self.deleted_at is not None
