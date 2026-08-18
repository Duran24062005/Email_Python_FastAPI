"""Tests unitarios de app/services/auth_service.py usando fakes."""

import pytest
from fastapi import HTTPException

from app.core.exceptions import EmailAlreadyExists
from app.core.security import hash_password, verify_password, decode_access_token
from app.models.user_models import UserStatus
from app.schemas.user_schemas import UserCreate, LoginRequest, ChangePasswordRequest
from app.services.auth_service import AuthService

from tests.conftest import FakeUserRepository, FakeSender, FakeTemplateEngine, make_user


def build_service(
    user_repo: FakeUserRepository | None = None,
    sender: FakeSender | None = None,
    template_engine: FakeTemplateEngine | None = None,
) -> AuthService:
    return AuthService(
        repository=user_repo or FakeUserRepository(),
        sender=sender,
        template_engine=template_engine,
    )


def make_active_user(email="juan@example.com", password="securepass123", **overrides):
    # make_user ya asigna status=UserStatus.ACTIVE por defecto
    return make_user(
        email=email,
        hash_password=hash_password(password),
        **overrides,
    )


# ── register ───────────────────────────────────────────────

async def test_register_creates_user_with_hashed_password_and_sends_email(fake_sender):
    repo = FakeUserRepository()
    service = build_service(repo, fake_sender, FakeTemplateEngine())

    response = await service.register(UserCreate(
        name="Juan", email="juan@example.com", password="securepass123"
    ))

    assert response.id is not None
    assert response.email == "juan@example.com"

    user = await repo.get_by_email("juan@example.com")
    assert user.hash_password != "securepass123"
    assert verify_password("securepass123", user.hash_password) is True

    assert len(fake_sender.sent) == 1
    assert fake_sender.sent[0]["subject"] == "Verifica tu cuenta"
    assert fake_sender.sent[0]["recipient"] == "juan@example.com"


async def test_register_duplicate_email_raises():
    existing = make_active_user()
    repo = FakeUserRepository([existing])
    service = build_service(repo)

    with pytest.raises(EmailAlreadyExists):
        await service.register(UserCreate(
            name="Otro", email="juan@example.com", password="securepass123"
        ))


async def test_register_without_sender_does_not_crash():
    repo = FakeUserRepository()
    service = build_service(repo, sender=None, template_engine=None)

    response = await service.register(UserCreate(
        name="Juan", email="juan@example.com", password="securepass123"
    ))

    assert response.id is not None


async def test_register_with_missing_verification_template_does_not_crash():
    repo = FakeUserRepository()
    engine = FakeTemplateEngine(missing={"welcome_educonnect.html"})
    service = build_service(repo, FakeSender(), engine)

    response = await service.register(UserCreate(
        name="Juan", email="juan@example.com", password="securepass123"
    ))

    assert response.id is not None


# ── login ──────────────────────────────────────────────────

async def test_login_success_returns_token_and_updates_last_login():
    repo = FakeUserRepository([make_active_user()])
    service = build_service(repo)

    result = await service.login(LoginRequest(
        email="juan@example.com", password="securepass123"
    ))

    assert result.access_token
    payload = decode_access_token(result.access_token)
    assert payload["sub"] == str(result.user.id)
    assert result.user.email == "juan@example.com"

    user = await repo.get_by_id(result.user.id)
    assert user.last_login is not None


async def test_login_wrong_password_raises_401():
    repo = FakeUserRepository([make_active_user()])
    service = build_service(repo)

    with pytest.raises(HTTPException) as exc_info:
        await service.login(LoginRequest(
            email="juan@example.com", password="password-incorrecta"
        ))
    assert exc_info.value.status_code == 401


async def test_login_unknown_email_raises_401():
    service = build_service(FakeUserRepository())

    with pytest.raises(HTTPException) as exc_info:
        await service.login(LoginRequest(
            email="nadie@example.com", password="securepass123"
        ))
    assert exc_info.value.status_code == 401


async def test_login_blocked_user_raises_403():
    repo = FakeUserRepository([make_active_user(status=UserStatus.BLOCKED)])
    service = build_service(repo)

    with pytest.raises(HTTPException) as exc_info:
        await service.login(LoginRequest(
            email="juan@example.com", password="securepass123"
        ))
    assert exc_info.value.status_code == 403
    assert "bloqueado" in exc_info.value.detail.lower()


async def test_login_pending_user_raises_403():
    repo = FakeUserRepository([make_active_user(status=UserStatus.PENDING)])
    service = build_service(repo)

    with pytest.raises(HTTPException) as exc_info:
        await service.login(LoginRequest(
            email="juan@example.com", password="securepass123"
        ))
    assert exc_info.value.status_code == 403
    assert "pendiente" in exc_info.value.detail.lower()


# ── change_password ────────────────────────────────────────

async def test_change_password_success():
    repo = FakeUserRepository([make_active_user()])
    service = build_service(repo)
    user = await repo.get_by_email("juan@example.com")

    result = await service.change_password(user.id, ChangePasswordRequest(
        current_password="securepass123", new_password="nueva-pass-segura"
    ))

    assert result["message"] == "Contraseña actualizada correctamente"
    refreshed = await repo.get_by_id(user.id)
    assert verify_password("nueva-pass-segura", refreshed.hash_password) is True


async def test_change_password_wrong_current_raises_400():
    repo = FakeUserRepository([make_active_user()])
    service = build_service(repo)
    user = await repo.get_by_email("juan@example.com")

    with pytest.raises(HTTPException) as exc_info:
        await service.change_password(user.id, ChangePasswordRequest(
            current_password="incorrecta", new_password="nueva-pass-segura"
        ))
    assert exc_info.value.status_code == 400
