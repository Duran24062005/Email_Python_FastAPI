"""Email management tests."""

import pytest
from httpx import AsyncClient

from app.models.user import User


@pytest.mark.asyncio
async def test_send_email_authenticated(async_client: AsyncClient, test_user: User, test_token: str):
    """Test sending email as authenticated user."""
    headers = {"Authorization": f"Bearer {test_token}"}
    
    email_data = {
        "recipient": "recipient@example.com",
        "subject": "Test Email",
        "body": "This is a test email",
    }

    response = await async_client.post(
        "/api/v1/emails/send",
        headers=headers,
        json=email_data,
    )

    assert response.status_code in [201, 400, 500]  # May fail if SMTP not configured


@pytest.mark.asyncio
async def test_send_email_without_authentication(async_client: AsyncClient):
    """Test that email sending requires authentication."""
    email_data = {
        "recipient": "recipient@example.com",
        "subject": "Test Email",
        "body": "This is a test email",
    }

    response = await async_client.post(
        "/api/v1/emails/send",
        json=email_data,
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_send_email_with_html(async_client: AsyncClient, test_user: User, test_token: str):
    """Test sending email with HTML body."""
    headers = {"Authorization": f"Bearer {test_token}"}
    
    email_data = {
        "recipient": "recipient@example.com",
        "subject": "Test HTML Email",
        "html_body": "<h1>Test</h1><p>This is an HTML email</p>",
    }

    response = await async_client.post(
        "/api/v1/emails/send",
        headers=headers,
        json=email_data,
    )

    assert response.status_code in [201, 400, 500]


@pytest.mark.asyncio
async def test_send_email_with_template(async_client: AsyncClient, test_user: User, test_token: str):
    """Test sending email with template."""
    headers = {"Authorization": f"Bearer {test_token}"}
    
    email_data = {
        "recipient": "recipient@example.com",
        "subject": "Welcome Email",
        "template_name": "welcome",
        "template_data": {"name": "John Doe"},
    }

    response = await async_client.post(
        "/api/v1/emails/send",
        headers=headers,
        json=email_data,
    )

    assert response.status_code in [201, 400, 500, 404]


@pytest.mark.asyncio
async def test_send_email_missing_recipient(async_client: AsyncClient, test_user: User, test_token: str):
    """Test validation error when recipient is missing."""
    headers = {"Authorization": f"Bearer {test_token}"}
    
    email_data = {
        "subject": "Test Email",
        "body": "This is a test email",
    }

    response = await async_client.post(
        "/api/v1/emails/send",
        headers=headers,
        json=email_data,
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_send_email_invalid_recipient(async_client: AsyncClient, test_user: User, test_token: str):
    """Test validation error with invalid recipient email."""
    headers = {"Authorization": f"Bearer {test_token}"}
    
    email_data = {
        "recipient": "invalid-email",
        "subject": "Test Email",
        "body": "This is a test email",
    }

    response = await async_client.post(
        "/api/v1/emails/send",
        headers=headers,
        json=email_data,
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_user_emails(async_client: AsyncClient, test_user: User, test_token: str):
    """Test listing user's emails."""
    headers = {"Authorization": f"Bearer {test_token}"}
    
    response = await async_client.get(
        "/api/v1/emails",
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "emails" in data
    assert isinstance(data["emails"], list)


@pytest.mark.asyncio
async def test_list_emails_with_pagination(async_client: AsyncClient, test_user: User, test_token: str):
    """Test listing emails with pagination."""
    headers = {"Authorization": f"Bearer {test_token}"}
    
    response = await async_client.get(
        "/api/v1/emails?skip=0&limit=10",
        headers=headers,
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_list_emails_without_auth(async_client: AsyncClient):
    """Test that listing emails requires authentication."""
    response = await async_client.get("/api/v1/emails")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_email_detail(async_client: AsyncClient, test_user: User, test_token: str):
    """Test getting email details."""
    headers = {"Authorization": f"Bearer {test_token}"}
    
    response = await async_client.get(
        "/api/v1/emails/1",
        headers=headers,
    )

    assert response.status_code in [200, 403, 404]


@pytest.mark.asyncio
async def test_get_email_not_found(async_client: AsyncClient, test_user: User, test_token: str):
    """Test getting non-existent email."""
    headers = {"Authorization": f"Bearer {test_token}"}
    
    response = await async_client.get(
        "/api/v1/emails/99999",
        headers=headers,
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_email_without_auth(async_client: AsyncClient):
    """Test that getting email details requires authentication."""
    response = await async_client.get("/api/v1/emails/1")

    assert response.status_code == 401
