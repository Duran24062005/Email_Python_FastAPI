"""Tests de los middlewares de autenticación y roles."""

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.core.security import create_access_token
from app.middlewares.auth_middleware import get_current_active_user, get_current_user
from app.middlewares.role_middleware import require_admin
from app.models.user_models import UserRole, UserStatus
from app.repositories.user_repository import UserRepository

from tests.conftest import make_user


# ── get_current_active_user ────────────────────────────────

async def test_get_current_active_user_allows_active():
    user = make_user(status=UserStatus.ACTIVE)
    assert await get_current_active_user(user) is user


@pytest.mark.parametrize("status", [UserStatus.PENDING, UserStatus.BLOCKED, UserStatus.UNACTIVE])
async def test_get_current_active_user_rejects_inactive(status):
    user = make_user(status=status)
    with pytest.raises(HTTPException) as exc_info:
        await get_current_active_user(user)
    assert exc_info.value.status_code == 403


# ── require_admin ──────────────────────────────────────────

async def test_require_admin_allows_admin():
    user = make_user(role=UserRole.ADMIN)
    assert await require_admin(user) is user


async def test_require_admin_rejects_general():
    user = make_user(role=UserRole.GENERAL)
    with pytest.raises(HTTPException) as exc_info:
        await require_admin(user)
    assert exc_info.value.status_code == 403


# ── get_current_user (JWT + repositorio) ───────────────────

async def test_get_current_user_with_valid_token(db_session):
    repo = UserRepository(db_session)
    user = await repo.create_with_hash("Ana", "ana@example.com", "hash")
    token = create_access_token({"sub": str(user.id)})

    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    current = await get_current_user(credentials=credentials, db=db_session)

    assert current.id == user.id


async def test_get_current_user_with_invalid_token(db_session):
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="token-roto")
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(credentials=credentials, db=db_session)
    assert exc_info.value.status_code == 401


async def test_get_current_user_with_expired_token(db_session):
    token = create_access_token(
        {"sub": "1"}, expires_delta=__import__("datetime").timedelta(seconds=-10)
    )
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(credentials=credentials, db=db_session)
    assert exc_info.value.status_code == 401
    assert "expirado" in exc_info.value.detail.lower()


async def test_get_current_user_with_unknown_user(db_session):
    token = create_access_token({"sub": "9999"})
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(credentials=credentials, db=db_session)
    assert exc_info.value.status_code == 401
