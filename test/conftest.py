"""Test configuration and fixtures."""

import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from app.config.config import app_config
from app.models.base import Base
# Explicitly import all models so they get registered with Base
from app.models.user import User, UserStatus
from app.models.role import Role
from app.models.permission import Permission
from app.models.email_model import Email
from app.models.team import Team
from app.config.database.connection import get_db
from app.core.security import create_access_token, create_refresh_token, hash_password
from app.main import app
from app.repositories.user import UserRepository


# Test database configuration
TEST_SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def test_db():
    """Create a test database."""
    engine = create_async_engine(
        TEST_SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def override_get_db():
        async with AsyncSession(engine, expire_on_commit=False) as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_db) -> AsyncGenerator[AsyncSession, None]:
    """Get database session for individual tests."""
    async with AsyncSession(test_db, expire_on_commit=False) as session:
        yield session


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user with ACTIVE status."""
    user_repo = UserRepository(db_session)
    user = await user_repo.create(
        email="testuser@example.com",
        hashed_password=hash_password("TestPass123!"),
        first_name="Test",
        last_name="User",
        _status=UserStatus.ACTIVE.value,
    )
    user.email_verified_at = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
    await db_session.flush()
    return await user_repo.get_with_roles_and_permissions(user.id)  # type: ignore


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession, test_user: User) -> User:
    """Create an admin user with ADMIN role."""
    from app.models.role import Role
    from sqlalchemy import select
    
    user_repo = UserRepository(db_session)
    admin = await user_repo.create(
        email="admin@example.com",
        hashed_password=hash_password("AdminPass123!"),
        first_name="Admin",
        last_name="User",
        _status=UserStatus.ACTIVE.value,
    )
    admin.email_verified_at = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
    await db_session.flush()
    
    # Create admin role if it doesn't exist
    result = await db_session.execute(select(Role).where(Role.name == "admin"))
    admin_role = result.scalars().first()
    
    if not admin_role:
        admin_role = Role(name="admin", description="Administrator role")
        db_session.add(admin_role)
        await db_session.flush()
    
    # Insert relationship directly using SQL to avoid lazy loading issues
    from sqlalchemy import text
    await db_session.execute(
        text("INSERT INTO user_role (user_id, role_id) VALUES (:user_id, :role_id)"),
        {"user_id": admin.id, "role_id": admin_role.id}
    )
    await db_session.commit()
    
    return await user_repo.get_with_roles_and_permissions(admin.id)  # type: ignore


@pytest_asyncio.fixture
async def test_token(test_user: User) -> str:
    """Create a valid JWT access token for test user."""
    return create_access_token(
        data={"sub": str(test_user.id)},
        roles=[role.name for role in test_user.roles],
        permissions=list(test_user.get_all_permissions()),
    )


@pytest_asyncio.fixture
async def admin_token(admin_user: User) -> str:
    """Create a valid JWT access token for admin user."""
    return create_access_token(
        data={"sub": str(admin_user.id)},
        roles=[role.name for role in admin_user.roles],
        permissions=list(admin_user.get_all_permissions()),
    )


@pytest_asyncio.fixture
async def refresh_token(test_user: User) -> str:
    """Create a valid JWT refresh token for test user."""
    return create_refresh_token(
        data={"sub": str(test_user.id)},
    )


@pytest_asyncio.fixture
async def async_client(test_db) -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP client for testing."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for the test session."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()
