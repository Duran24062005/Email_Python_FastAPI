"""Authentication service with JWT token management."""

from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.models.user import User, UserStatus
from app.repositories.user import UserRepository


class AuthService:
    """Service class for authentication operations."""

    async def authenticate_user(
        self,
        db: AsyncSession,
        email: str,
        password: str,
    ) -> tuple[str, str, User, int]:
        """
        Authenticate user with email and password.

        Returns:
            Tuple of (access_token, refresh_token, user, expires_in_seconds)

        Raises:
            UnauthorizedError: If credentials are invalid
        """
        user_repo = UserRepository(db)
        user = await user_repo.get_by_email_with_roles(email)

        if user is None:
            raise UnauthorizedError("Invalid email or password")

        # Verify password
        if not verify_password(password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password")

        # Check if user account is active
        if user.deleted_at is not None:
            raise UnauthorizedError("User account has been deleted")

        if user.status != UserStatus.ACTIVE:
            if user.status == UserStatus.PENDING_VERIFICATION:
                raise UnauthorizedError(
                    "Email verification required. Please verify your email to activate your account."
                )
            raise UnauthorizedError(
                f"User account is {user.status.value}. Please verify your email."
            )

        # Create tokens
        role_names = [role.name for role in user.roles]
        permissions = user.get_all_permissions()

        access_token = create_access_token(
            data={"sub": str(user.id)},
            roles=role_names,
            permissions=list(permissions),
        )

        refresh_token = create_refresh_token(
            data={"sub": str(user.id)},
        )

        # Get expiration time in seconds
        from app.config.config import security_config

        expires_in = security_config["ACCESS_TOKEN_EXPIRE_MINUTES"] * 60

        return access_token, refresh_token, user, expires_in

    async def refresh_access_token(
        self,
        db: AsyncSession,
        refresh_token: str,
    ) -> tuple[str, int]:
        """
        Generate a new access token using a refresh token.

        Returns:
            Tuple of (new_access_token, expires_in_seconds)

        Raises:
            UnauthorizedError: If refresh token is invalid or expired
        """
        # Decode refresh token
        payload = decode_token(refresh_token)
        if payload is None:
            raise UnauthorizedError("Invalid or expired refresh token")

        if payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid token type. Expected refresh token.")

        user_id = payload.get("sub")
        if user_id is None:
            raise UnauthorizedError("Invalid token payload")

        # Get user with roles
        user_repo = UserRepository(db)
        user = await user_repo.get_with_roles(int(user_id))

        if user is None:
            raise UnauthorizedError("User not found")

        # Check if user account is still active
        if user.deleted_at is not None:
            raise UnauthorizedError("User account has been deleted")

        if user.status != UserStatus.ACTIVE:
            raise UnauthorizedError("User account is not active")

        # Create new access token
        role_names = [role.name for role in user.roles]
        permissions = user.get_all_permissions()

        new_access_token = create_access_token(
            data={"sub": str(user.id)},
            roles=role_names,
            permissions=list(permissions),
        )

        # Get expiration time in seconds
        from app.config.config import security_config

        expires_in = security_config["ACCESS_TOKEN_EXPIRE_MINUTES"] * 60

        return new_access_token, expires_in

    async def verify_token(
        self,
        db: AsyncSession,
        token: str,
    ) -> tuple[bool, User | None]:
        """
        Verify a JWT token and return user if valid.

        Returns:
            Tuple of (is_valid, user_or_none)
        """
        # Decode token
        payload = decode_token(token)
        if payload is None:
            return False, None

        # Only accept access tokens, not refresh tokens
        if payload.get("type") != "access":
            return False, None

        user_id = payload.get("sub")
        if user_id is None:
            return False, None

        # Get user with roles
        user_repo = UserRepository(db)
        user = await user_repo.get_with_roles(int(user_id))

        if user is None:
            return False, None

        # Check if user account is still active
        if user.deleted_at is not None:
            return False, None

        if user.status != UserStatus.ACTIVE:
            return False, None

        return True, user


# Singleton instance
auth_service = AuthService()