"""Imports convenientes para registrar metadata de SQLAlchemy."""

from app.models.email_model import Email, EmailStatus
from app.models.user_models import User, UserRole, UserStatus

__all__ = [
    "Email",
    "EmailStatus",
    "User",
    "UserRole",
    "UserStatus",
]
