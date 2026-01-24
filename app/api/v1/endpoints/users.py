"""User API endpoints."""

from fastapi import APIRouter, Query, status

from app.api.deps import CurrentActiveUser, DBSession, RequireAdmin
from app.core.exceptions import (
    AlreadyExistsError,
    NotFoundError,
    ValidationError,
    http_bad_request,
    http_conflict,
    http_forbidden,
    http_not_found,
)
from app.models.user import UserStatus
from app.schemas.common import Message, PaginatedResponse
from app.schemas.user import (
    AssignRoleRequest,
    EmailVerificationRequest,
    UserAdminResponse,
    UserCreate,
    UserUpdate,
    UserWithRolesResponse,
)
from app.services.user import user_service

router = APIRouter()


# ============================================================================
# Public Endpoints
# ============================================================================


@router.post(
    "/register",
    response_model=UserWithRolesResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account. Email verification will be required.",
)
async def register_user(
    user_data: UserCreate,
    db: DBSession,
) -> UserWithRolesResponse:
    """Register a new user account."""
    try:
        user, verification_token = await user_service.register_user(db, user_data)
        # TODO: Send verification email with token
        # For now, we'll just return the user (token would be sent via email)
        return UserWithRolesResponse.model_validate(user)
    except AlreadyExistsError as e:
        raise http_conflict(e.message)


@router.post(
    "/verify-email",
    response_model=Message,
    summary="Verify email address",
    description="Verify user's email using the token sent via email.",
)
async def verify_email(
    request: EmailVerificationRequest,
    db: DBSession,
) -> Message:
    """Verify user's email address."""
    try:
        await user_service.verify_email(db, request.token)
        return Message(message="Email verified successfully")
    except ValidationError as e:
        raise http_bad_request(e.message)
    except NotFoundError as e:
        raise http_not_found(e.message)


# ============================================================================
# Protected Endpoints (Authenticated Users)
# ============================================================================


@router.get(
    "/me",
    response_model=UserWithRolesResponse,
    summary="Get current user",
    description="Get the profile of the currently authenticated user.",
)
async def get_current_user_profile(
    current_user: CurrentActiveUser,
) -> UserWithRolesResponse:
    """Get current authenticated user's profile."""
    return UserWithRolesResponse.model_validate(current_user)


@router.patch(
    "/me",
    response_model=UserWithRolesResponse,
    summary="Update current user",
    description="Update the profile of the currently authenticated user.",
)
async def update_current_user_profile(
    user_data: UserUpdate,
    db: DBSession,
    current_user: CurrentActiveUser,
) -> UserWithRolesResponse:
    """Update current authenticated user's profile."""
    try:
        user = await user_service.update_user(db, current_user.id, user_data)
        return UserWithRolesResponse.model_validate(user)
    except NotFoundError as e:
        raise http_not_found(e.message)


# ============================================================================
# Admin Endpoints
# ============================================================================


@router.get(
    "",
    response_model=PaginatedResponse[UserAdminResponse],
    summary="List users (Admin)",
    description="Get a paginated list of all users. Requires admin role.",
)
async def list_users(
    db: DBSession,
    current_user: CurrentActiveUser,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status_filter: UserStatus | None = Query(None, alias="status", description="Filter by status"),
    include_deleted: bool = Query(False, description="Include soft-deleted users"),
) -> PaginatedResponse[UserAdminResponse]:
    """List all users with pagination."""
    # Check admin permission
    if not current_user.has_role("admin"):
        raise http_forbidden("Admin role required")
    
    skip = (page - 1) * page_size
    users, total = await user_service.get_users(
        db,
        skip=skip,
        limit=page_size,
        include_deleted=include_deleted,
        status=status_filter,
    )

    pages = (total + page_size - 1) // page_size  # Ceiling division

    return PaginatedResponse[UserAdminResponse](
        items=[UserAdminResponse.model_validate(u) for u in users],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get(
    "/{user_id}",
    response_model=UserAdminResponse,
    summary="Get user by ID (Admin)",
    description="Get a specific user by their ID. Requires admin role.",
)
async def get_user(
    user_id: int,
    db: DBSession,
    current_user: CurrentActiveUser,
) -> UserAdminResponse:
    """Get a user by ID."""
    # Check admin permission
    if not current_user.has_role("admin"):
        raise http_forbidden("Admin role required")
    
    try:
        user = await user_service.get_user(db, user_id)
        return UserAdminResponse.model_validate(user)
    except NotFoundError as e:
        raise http_not_found(e.message)


@router.delete(
    "/{user_id}",
    response_model=Message,
    summary="Delete user (Admin)",
    description="Soft delete a user. Requires admin role.",
)
async def delete_user(
    user_id: int,
    db: DBSession,
    current_user: CurrentActiveUser,
) -> Message:
    """Soft delete a user."""
    # Check admin permission
    if not current_user.has_role("admin"):
        raise http_forbidden("Admin role required")
    
    # Prevent self-deletion
    if user_id == current_user.id:
        raise http_bad_request("Cannot delete your own account")

    try:
        await user_service.soft_delete_user(db, user_id)
        return Message(message="User deleted successfully")
    except NotFoundError as e:
        raise http_not_found(e.message)


@router.post(
    "/{user_id}/roles",
    response_model=UserWithRolesResponse,
    summary="Assign role to user (Admin)",
    description="Assign a role to a user. Requires admin role.",
)
async def assign_role_to_user(
    user_id: int,
    request: AssignRoleRequest,
    db: DBSession,
    current_user: CurrentActiveUser,
) -> UserWithRolesResponse:
    """Assign a role to a user."""
    # Check admin permission
    if not current_user.has_role("admin"):
        raise http_forbidden("Admin role required")
    
    try:
        user = await user_service.assign_role(db, user_id, request.role_id)
        return UserWithRolesResponse.model_validate(user)
    except NotFoundError as e:
        raise http_not_found(e.message)


@router.delete(
    "/{user_id}/roles/{role_id}",
    response_model=UserWithRolesResponse,
    summary="Remove role from user (Admin)",
    description="Remove a role from a user. Requires admin role.",
)
async def remove_role_from_user(
    user_id: int,
    role_id: int,
    db: DBSession,
    current_user: CurrentActiveUser,
) -> UserWithRolesResponse:
    """Remove a role from a user."""
    # Check admin permission
    if not current_user.has_role("admin"):
        raise http_forbidden("Admin role required")
    
    try:
        user = await user_service.remove_role(db, user_id, role_id)
        return UserWithRolesResponse.model_validate(user)
    except NotFoundError as e:
        raise http_not_found(e.message)