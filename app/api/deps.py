"""Common API dependencies for authentication and database access."""

from collections.abc import Awaitable, Callable
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import http_forbidden, http_unauthorized
from app.core.security import decode_token
from app.config.database.connection import get_db
from app.models.user import User, UserStatus
from app.repositories.user import UserRepository

# Security scheme for JWT Bearer tokens
security = HTTPBearer(auto_error=False)

# Type alias for database session dependency
DBSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    db: DBSession,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.

    Raises:
        HTTPException 401: If token is missing, invalid, or expired
        HTTPException 401: If user not found
    """
    if credentials is None:
        raise http_unauthorized("Missing authentication token")

    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise http_unauthorized("Invalid or expired token")

    # Check token type
    if payload.get("type") != "access":
        raise http_unauthorized("Invalid token type")

    user_id = payload.get("sub")
    if user_id is None:
        raise http_unauthorized("Invalid token payload")

    user_repo = UserRepository(db)
    user = await user_repo.get_with_roles(int(user_id))

    if user is None:
        raise http_unauthorized("User not found")

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Dependency to get the current user and verify they are active.

    Raises:
        HTTPException 403: If user account is not active
    """
    if current_user.deleted_at is not None:
        raise http_forbidden("Account has been deleted")

    if current_user.status != UserStatus.ACTIVE:
        if current_user.status == UserStatus.PENDING_VERIFICATION:
            raise http_forbidden("Email verification required")
        elif current_user.status == UserStatus.SUSPENDED:
            raise http_forbidden("Account has been suspended")
        elif current_user.status == UserStatus.INACTIVE:
            raise http_forbidden("Account is inactive")
        else:
            raise http_forbidden("Account is not active")

    return current_user


def require_permission(
    permission_code: str,
) -> Callable[[Annotated[User, Depends(get_current_active_user)]], Awaitable[User]]:
    """
    Factory for creating a dependency that checks if user has a specific permission.

    Usage:
        @router.get("/admin", dependencies=[Depends(require_permission("admin.access"))])
        async def admin_endpoint(): ...
    """

    async def permission_checker(
        current_user: Annotated[User, Depends(get_current_active_user)],
    ) -> User:
        if not current_user.has_permission(permission_code):
            raise http_forbidden(f"Permission '{permission_code}' required")
        return current_user

    return permission_checker


def require_role(
    role_name: str,
) -> Callable[[Annotated[User, Depends(get_current_active_user)]], Awaitable[User]]:
    """
    Factory for creating a dependency that checks if user has a specific role.

    Usage:
        @router.get("/admin", dependencies=[Depends(require_role("admin"))])
        async def admin_endpoint(): ...
    """

    async def role_checker(
        current_user: Annotated[User, Depends(get_current_active_user)],
    ) -> User:
        if not current_user.has_role(role_name):
            raise http_forbidden(f"Role '{role_name}' required")
        return current_user

    return role_checker


# Type aliases for common dependency patterns
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentActiveUser = Annotated[User, Depends(get_current_active_user)]

# Pre-built admin dependency
RequireAdmin = Depends(require_role("admin"))