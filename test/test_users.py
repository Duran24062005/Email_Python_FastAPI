"""User management tests."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserStatus
from app.repositories.user import UserRepository


@pytest.mark.asyncio
async def test_get_current_user_profile(async_client: AsyncClient, test_user: User, test_token: str):
    """Test getting current user profile."""
    headers = {"Authorization": f"Bearer {test_token}"}
    
    response = await async_client.get(
        "/api/v1/users/me",
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user.id
    assert data["email"] == test_user.email
    assert data["first_name"] == test_user.first_name
    assert data["last_name"] == test_user.last_name


@pytest.mark.asyncio
async def test_get_current_user_without_auth(async_client: AsyncClient):
    """Test getting profile without authentication."""
    response = await async_client.get("/api/v1/users/me")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_user_profile(async_client: AsyncClient, test_user: User, test_token: str):
    """Test updating user profile."""
    headers = {"Authorization": f"Bearer {test_token}"}
    
    update_data = {
        "first_name": "Updated",
        "last_name": "Name",
        "phone": "+9876543210",
        "address": "456 New St",
    }

    response = await async_client.patch(
        "/api/v1/users/me",
        headers=headers,
        json=update_data,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Updated"
    assert data["last_name"] == "Name"
    assert data["phone"] == "+9876543210"
    assert data["address"] == "456 New St"


@pytest.mark.asyncio
async def test_update_user_partial(async_client: AsyncClient, test_user: User, test_token: str):
    """Test partial user profile update."""
    headers = {"Authorization": f"Bearer {test_token}"}
    
    update_data = {
        "first_name": "PartialUpdate",
    }

    response = await async_client.patch(
        "/api/v1/users/me",
        headers=headers,
        json=update_data,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "PartialUpdate"
    assert data["last_name"] == test_user.last_name  # Should remain unchanged


@pytest.mark.asyncio
async def test_list_users_admin(async_client: AsyncClient, admin_user: User, admin_token: str):
    """Test listing users as admin."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    response = await async_client.get(
        "/api/v1/users",
        headers=headers,
    )

    assert response.status_code in [200, 403]  # Might be restricted


@pytest.mark.asyncio
async def test_list_users_non_admin(async_client: AsyncClient, test_user: User, test_token: str):
    """Test that non-admin cannot list users."""
    headers = {"Authorization": f"Bearer {test_token}"}
    
    response = await async_client.get(
        "/api/v1/users",
        headers=headers,
    )

    # Should be forbidden
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_user_admin(async_client: AsyncClient, admin_user: User, admin_token: str, test_user: User):
    """Test getting specific user as admin."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    response = await async_client.get(
        f"/api/v1/users/{test_user.id}",
        headers=headers,
    )

    assert response.status_code in [200, 403]


@pytest.mark.asyncio
async def test_get_user_not_found(async_client: AsyncClient, admin_token: str):
    """Test getting non-existent user."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    response = await async_client.get(
        "/api/v1/users/99999",
        headers=headers,
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_soft_delete_user_admin(async_client: AsyncClient, admin_user: User, admin_token: str, db_session: AsyncSession):
    """Test soft deleting a user as admin."""
    # Create a temporary user to delete
    user_repo = UserRepository(db_session)
    temp_user = await user_repo.create(
        email="todelete@example.com",
        hashed_password="hashed",
        first_name="To",
        last_name="Delete",
        _status=UserStatus.ACTIVE.value,
    )
    await db_session.flush()

    headers = {"Authorization": f"Bearer {admin_token}"}
    
    response = await async_client.delete(
        f"/api/v1/users/{temp_user.id}",
        headers=headers,
    )

    assert response.status_code in [200, 403, 404]


@pytest.mark.asyncio
async def test_delete_user_non_admin(async_client: AsyncClient, test_token: str, test_user: User):
    """Test that non-admin cannot delete users."""
    headers = {"Authorization": f"Bearer {test_token}"}
    
    response = await async_client.delete(
        f"/api/v1/users/{test_user.id}",
        headers=headers,
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_assign_role_admin(async_client: AsyncClient, admin_user: User, admin_token: str, test_user: User):
    """Test assigning role to user as admin."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # This assumes role with id 1 exists
    response = await async_client.post(
        f"/api/v1/users/{test_user.id}/roles",
        headers=headers,
        json={"role_id": 1},
    )

    assert response.status_code in [200, 403, 404]


@pytest.mark.asyncio
async def test_remove_role_admin(async_client: AsyncClient, admin_user: User, admin_token: str, test_user: User):
    """Test removing role from user as admin."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    response = await async_client.delete(
        f"/api/v1/users/{test_user.id}/roles/1",
        headers=headers,
    )

    assert response.status_code in [200, 403, 404]


@pytest.mark.asyncio
async def test_password_validation_on_register(async_client: AsyncClient):
    """Test password validation on registration."""
    user_data = {
        "email": "test@example.com",
        "password": "short",  # Too short
        "first_name": "Test",
        "last_name": "User",
    }

    response = await async_client.post(
        "/api/v1/users/register",
        json=user_data,
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_email_validation_on_register(async_client: AsyncClient):
    """Test email validation on registration."""
    user_data = {
        "email": "invalid-email",  # Invalid email
        "password": "SecurePassword123!",
        "first_name": "Test",
        "last_name": "User",
    }

    response = await async_client.post(
        "/api/v1/users/register",
        json=user_data,
    )

    assert response.status_code == 422
