"""Security utilities for authentication and authorization."""

from datetime import timezone, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
import bcrypt

from app.config.config import security_config
UTC = timezone.utc


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
    roles: list[str] | None = None,
    permissions: list[str] | None = None,
) -> str:
    """Create a JWT access token.

    Args:
        data: Base token payload (must include 'sub' for user_id)
        expires_delta: Optional custom expiration time
        roles: Optional list of role names to include in token
        permissions: Optional list of permission codes to include in token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=security_config["ACCESS_TOKEN_EXPIRE_MINUTES"])

    to_encode["exp"] = expire
    # Only set type to "access" if not already specified
    if "type" not in to_encode:
        to_encode["type"] = "access"

    # Include roles and permissions if provided
    if roles is not None:
        to_encode["roles"] = roles
    if permissions is not None:
        to_encode["permissions"] = permissions

    encoded: str = jwt.encode(to_encode, security_config["SECRET_KEY"], algorithm=security_config["ALGORITHM"])
    return encoded


def create_refresh_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(days=security_config["REFRESH_TOKEN_EXPIRE_DAYS"])

    to_encode.update({"exp": expire, "type": "refresh"})
    encoded: str = jwt.encode(to_encode, security_config["SECRET_KEY"], algorithm=security_config["ALGORITHM"])
    return encoded


def decode_token(token: str) -> dict[str, Any] | None:
    """Decode and validate a JWT token."""
    try:
        payload: dict[str, Any] = jwt.decode(
            token,
            security_config["SECRET_KEY"],
            algorithms=[security_config["ALGORITHM"]],
        )
        return payload
    except JWTError:
        return None