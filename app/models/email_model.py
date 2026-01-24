"""Email model for storing sent email records."""

import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class EmailStatus(str, enum.Enum):
    """Estados posibles de un email"""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class Email(Base, TimestampMixin):
    """Modelo de base de datos para emails"""
    __tablename__ = "emails"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    recipient: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    html_body: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[EmailStatus] = mapped_column(
        Enum(EmailStatus, name='emailstatus', create_type=False),
        default=EmailStatus.PENDING,
        nullable=False
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="emails")

    def __repr__(self) -> str:
        return f"<Email(id={self.id}, recipient='{self.recipient}', status={self.status})>"
