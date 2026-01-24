"""Authentication API endpoints."""

from fastapi import APIRouter, Response, status

from app.api.deps import CurrentActiveUser, DBSession
from app.core.exceptions import (
    UnauthorizedError,
    ValidationError,
    http_bad_request,
    http_unauthorized,
)
from app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    RefreshTokenResponse,
    TokenResponse,
    VerifyTokenRequest,
    VerifyTokenResponse,
)
from app.schemas.user import UserWithRolesResponse
from app.services.auth import auth_service

router = APIRouter()


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Login user",
    description="Authenticate user with email and password, returns JWT tokens.",
)
async def login(
    login_data: LoginRequest,
    db: DBSession,
) -> TokenResponse:
    """Authenticate user and return JWT tokens."""
    try:
        access_token, refresh_token, user, expires_in = await auth_service.authenticate_user(
            db, login_data.email, login_data.password
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=expires_in,
            user=UserWithRolesResponse.model_validate(user),
        )
    except UnauthorizedError as e:
        raise http_unauthorized(e.message)


@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="Generate a new access token using a valid refresh token.",
)
async def refresh_token(
    request: RefreshTokenRequest,
    db: DBSession,
) -> RefreshTokenResponse:
    """Refresh access token using refresh token."""
    try:
        access_token, expires_in = await auth_service.refresh_access_token(
            db, request.refresh_token
        )

        return RefreshTokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=expires_in,
        )
    except UnauthorizedError as e:
        raise http_unauthorized(e.message)
    except ValidationError as e:
        raise http_bad_request(e.message)


@router.post(
    "/verify",
    response_model=VerifyTokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify token",
    description="Verify if a JWT access token is valid and return user information.",
)
async def verify_token(
    request: VerifyTokenRequest,
    db: DBSession,
) -> VerifyTokenResponse:
    """Verify JWT token and return user information if valid."""
    is_valid, user = await auth_service.verify_token(db, request.token)

    if not is_valid or user is None:
        return VerifyTokenResponse(valid=False, user=None)

    return VerifyTokenResponse(
        valid=True,
        user=UserWithRolesResponse.model_validate(user),
    )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout user",
    description="Logout current authenticated user. Client should delete tokens locally.",
)
async def logout(
    current_user: CurrentActiveUser,
) -> Response:
    """Logout current user."""
    return Response(status_code=status.HTTP_200_OK)