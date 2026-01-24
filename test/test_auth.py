"""User authentication tests."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.user import User, UserStatus
from app.repositories.user import UserRepository
from app.services.auth import auth_service


@pytest.mark.asyncio
async def test_user_registration(async_client: AsyncClient):
    """Test user registration endpoint."""
    user_data = {
        "email": "testuser@example.com",
        "password": "SecurePassword123!",
        "first_name": "Test",
        "last_name": "User",
        "phone": "+1234567890",
        "address": "123 Test St",
    }

    response = await async_client.post(
        "/api/v1/users/register",
        json=user_data,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["first_name"] == user_data["first_name"]
    assert data["last_name"] == user_data["last_name"]
    assert "id" in data


@pytest.mark.asyncio
async def test_user_registration_duplicate_email(async_client: AsyncClient):
    """Test that duplicate email registration fails."""
    user_data = {
        "email": "duplicate@example.com",
        "password": "SecurePassword123!",
        "first_name": "Test",
        "last_name": "User",
    }

    # First registration should succeed
    response1 = await async_client.post(
        "/api/v1/users/register",
        json=user_data,
    )
    assert response1.status_code == 201

    # Second registration with same email should fail
    response2 = await async_client.post(
        "/api/v1/users/register",
        json=user_data,
    )
    assert response2.status_code == 409


@pytest.mark.asyncio
async def test_user_login_unverified_email(async_client: AsyncClient):
    """Test that login fails for unverified email."""
    user_data = {
        "email": "unverified@example.com",
        "password": "SecurePassword123!",
        "first_name": "Unverified",
        "last_name": "User",
    }

    # Register user (status is PENDING_VERIFICATION by default)
    await async_client.post("/api/v1/users/register", json=user_data)

    # Try to login - should fail
    login_data = {
        "email": user_data["email"],
        "password": user_data["password"],
    }

    response = await async_client.post(
        "/api/v1/auth/login",
        json=login_data,
    )

    assert response.status_code == 401
    data = response.json()
    assert "pending_verification" in data["detail"].lower() or "verify" in data["detail"].lower()


@pytest.mark.asyncio
async def test_user_login_verified(async_client: AsyncClient, db_session: AsyncSession, test_user: User):
    """Test successful login with verified user."""
    login_data = {
        "email": test_user.email,
        "password": "TestPass123!",
    }

    response = await async_client.post(
        "/api/v1/auth/login",
        json=login_data,
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == test_user.email
    assert "expires_in" in data


@pytest.mark.asyncio
async def test_user_login_invalid_credentials(async_client: AsyncClient):
    """Test login with invalid credentials."""
    login_data = {
        "email": "nonexistent@example.com",
        "password": "WrongPassword!",
    }

    response = await async_client.post(
        "/api/v1/auth/login",
        json=login_data,
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_user_login_wrong_password(async_client: AsyncClient, test_user: User):
    """Test login with correct email but wrong password."""
    login_data = {
        "email": test_user.email,
        "password": "WrongPassword123!",
    }

    response = await async_client.post(
        "/api/v1/auth/login",
        json=login_data,
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_token_refresh(async_client: AsyncClient, test_user: User, refresh_token: str):
    """Test refreshing access token with valid refresh token."""
    response = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "expires_in" in data


@pytest.mark.asyncio
async def test_token_refresh_invalid_token(async_client: AsyncClient):
    """Test refreshing with invalid refresh token."""
    response = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid_token_here"},
    )

    assert response.status_code in [401, 400]


@pytest.mark.asyncio
async def test_token_verify_valid(async_client: AsyncClient, test_token: str):
    """Test verifying a valid access token."""
    response = await async_client.post(
        "/api/v1/auth/verify",
        json={"token": test_token},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["user"] is not None
    assert "id" in data["user"]


@pytest.mark.asyncio
async def test_token_verify_invalid_token(async_client: AsyncClient):
    """Test verifying an invalid access token."""
    response = await async_client.post(
        "/api/v1/auth/verify",
        json={"token": "invalid_token_here"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert data["user"] is None


@pytest.mark.asyncio
async def test_token_verify_refresh_token(async_client: AsyncClient, refresh_token: str):
    """Test verifying with refresh token (should fail - only accepts access tokens)."""
    response = await async_client.post(
        "/api/v1/auth/verify",
        json={"token": refresh_token},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False


@pytest.mark.asyncio
async def test_logout(async_client: AsyncClient, test_user: User, test_token: str):
    """Test logout endpoint."""
    headers = {"Authorization": f"Bearer {test_token}"}
    
    response = await async_client.post(
        "/api/v1/auth/logout",
        headers=headers,
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_logout_without_auth(async_client: AsyncClient):
    """Test logout without authentication."""
    response = await async_client.post("/api/v1/auth/logout")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_email_verification_flow(async_client: AsyncClient, db_session: AsyncSession):
    """Test complete email verification flow."""
    # Register user
    user_data = {
        "email": "verify@example.com",
        "password": "SecurePassword123!",
        "first_name": "Verify",
        "last_name": "Test",
    }

    response = await async_client.post(
        "/api/v1/users/register",
        json=user_data,
    )

    assert response.status_code == 201
    registered_user_id = response.json()["id"]

    # Get verification token from user service
    from app.services.user import UserService
    user_service = UserService()
    user_repo = UserRepository(db_session)
    # Use get_with_roles to ensure user is found correctly
    user = await user_repo.get_with_roles(registered_user_id)
    assert user is not None
    verification_token = user_service._create_verification_token(user.id, user.email)

    # Verify email
    response = await async_client.post(
        "/api/v1/users/verify-email",
        json={"token": verification_token},
    )

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "verified" in data["message"].lower()

    # Now try to login - should succeed
    login_data = {
        "email": user_data["email"],
        "password": user_data["password"],
    }

    response = await async_client.post(
        "/api/v1/auth/login",
        json=login_data,
    )

    assert response.status_code == 200
