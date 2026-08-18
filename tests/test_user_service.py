"""Tests unitarios de app/services/user_service.py usando fakes."""

from datetime import timedelta

import pytest
from fastapi import HTTPException

from app.core.security import create_access_token
from app.models.user_models import UserStatus
from app.models.email_model import EmailStatus
from app.schemas.user_schemas import UserUpdate
from app.services.user_service import UserService

from tests.conftest import (
    FakeEmailRepository,
    FakeSender,
    FakeTemplateEngine,
    FakeUserRepository,
    make_email,
    make_user,
)


def build_service(
    user_repo: FakeUserRepository | None = None,
    email_repo: FakeEmailRepository | None = None,
    sender: FakeSender | None = None,
    template_engine: FakeTemplateEngine | None = None,
) -> UserService:
    return UserService(
        user_repository=user_repo or FakeUserRepository(),
        email_repository=email_repo or FakeEmailRepository(),
        sender=sender or FakeSender(),
        template_engine=template_engine,
    )


def make_user_with_id(user_id: int, **overrides) -> "make_user":
    return make_user(id=user_id, **overrides)


# ── Perfil e inbox ─────────────────────────────────────────

async def test_get_my_profile_found():
    repo = FakeUserRepository([make_user(id=1, name="Ana")])
    service = build_service(user_repo=repo)

    profile = await service.get_my_profile(1)

    assert profile.id == 1
    assert profile.name == "Ana"


async def test_get_my_profile_not_found_raises_404():
    service = build_service()

    with pytest.raises(HTTPException) as exc_info:
        await service.get_my_profile(999)
    assert exc_info.value.status_code == 404


async def test_get_my_inbox_paginates():
    email_repo = FakeEmailRepository([
        make_email(id=1, user_id=1),
        make_email(id=2, user_id=1),
        make_email(id=3, user_id=1),
        make_email(id=4, user_id=2),
    ])
    service = build_service(email_repo=email_repo)

    inbox = await service.get_my_inbox(1, page=1, page_size=2)

    assert inbox.total == 3
    assert len(inbox.emails) == 2
    assert inbox.page == 1


# ── resend_email ───────────────────────────────────────────

async def test_resend_email_creates_new_record_and_sends(fake_sender):
    email_repo = FakeEmailRepository([make_email(id=5, user_id=1, subject="Original")])
    service = build_service(email_repo=email_repo, sender=fake_sender)

    response = await service.resend_email(1, 5)

    assert response.id != 5
    assert response.subject == "Original"
    assert response.status == EmailStatus.SENT
    assert len(fake_sender.sent) == 1
    assert fake_sender.sent[0]["subject"] == "Original"


async def test_resend_email_not_found_raises_404():
    service = build_service()

    with pytest.raises(HTTPException) as exc_info:
        await service.resend_email(1, 999)
    assert exc_info.value.status_code == 404


async def test_resend_email_of_other_user_raises_403():
    email_repo = FakeEmailRepository([make_email(id=5, user_id=2)])
    service = build_service(email_repo=email_repo)

    with pytest.raises(HTTPException) as exc_info:
        await service.resend_email(1, 5)
    assert exc_info.value.status_code == 403


async def test_resend_email_when_sender_fails_marks_failed():
    email_repo = FakeEmailRepository([make_email(id=5, user_id=1)])
    service = build_service(email_repo=email_repo, sender=FakeSender(result=False))

    response = await service.resend_email(1, 5)

    assert response.status == EmailStatus.FAILED


async def test_resend_email_when_sender_raises_marks_failed_with_error():
    email_repo = FakeEmailRepository([make_email(id=5, user_id=1)])
    service = build_service(
        email_repo=email_repo, sender=FakeSender(error=RuntimeError("SMTP down"))
    )

    response = await service.resend_email(1, 5)

    assert response.status == EmailStatus.FAILED
    assert response.error_message == "SMTP down"


# ── send_email_with_template ───────────────────────────────

async def test_send_email_with_template_renders_and_sends(fake_sender, fake_template_engine):
    service = build_service(sender=fake_sender, template_engine=fake_template_engine)

    response = await service.send_email_with_template(
        user_id=1,
        recipient="cliente@example.com",
        subject="Oferta",
        template_name="welcome.html",
        template_data={"nombre": "Ana"},
    )

    assert response.status == EmailStatus.SENT
    assert fake_sender.sent[0]["html_body"] == "<html><body>rendered:welcome.html</body></html>"
    assert response.html_body == "<html><body>rendered:welcome.html</body></html>"


async def test_send_email_with_template_missing_raises_404():
    engine = FakeTemplateEngine(missing={"no-existe.html"})
    service = build_service(template_engine=engine)

    with pytest.raises(HTTPException) as exc_info:
        await service.send_email_with_template(
            user_id=1,
            recipient="cliente@example.com",
            subject="Oferta",
            template_name="no-existe.html",
            template_data={},
        )
    assert exc_info.value.status_code == 404


# ── save_email_key ─────────────────────────────────────────

async def test_save_email_key_updates_user():
    repo = FakeUserRepository([make_user(id=1)])
    service = build_service(user_repo=repo)

    result = await service.save_email_key(1, "xxxx xxxx xxxx xxxx")

    assert result["message"] == "Email key guardada correctamente"
    user = await repo.get_by_id(1)
    assert user.email_key == "xxxx xxxx xxxx xxxx"


# ── verify_email_token ─────────────────────────────────────

def verification_token(user_id: int, purpose: str = "email_verification", **kwargs) -> str:
    return create_access_token({"sub": str(user_id), "purpose": purpose}, **kwargs)


async def test_verify_email_token_valid():
    repo = FakeUserRepository([make_user(id=1, email_verify=False)])
    service = build_service(user_repo=repo)

    result = await service.verify_email_token(verification_token(1))

    assert result["message"] == "Email verificado exitosamente"
    user = await repo.get_by_id(1)
    assert user.email_verify is True


async def test_verify_email_token_already_verified():
    repo = FakeUserRepository([make_user(id=1, email_verify=True)])
    service = build_service(user_repo=repo)

    result = await service.verify_email_token(verification_token(1))

    assert result["message"] == "El email ya estaba verificado"


async def test_verify_email_token_wrong_purpose_raises_400():
    service = build_service(FakeUserRepository([make_user(id=1)]))

    with pytest.raises(HTTPException) as exc_info:
        await service.verify_email_token(verification_token(1, purpose="otro"))
    assert exc_info.value.status_code == 400


async def test_verify_email_token_expired_raises_400():
    service = build_service(FakeUserRepository([make_user(id=1)]))
    token = verification_token(1, expires_delta=timedelta(seconds=-10))

    with pytest.raises(HTTPException) as exc_info:
        await service.verify_email_token(token)
    assert exc_info.value.status_code == 400
    assert "expirado" in exc_info.value.detail.lower()


async def test_verify_email_token_invalid_raises_400():
    service = build_service(FakeUserRepository([make_user(id=1)]))

    with pytest.raises(HTTPException) as exc_info:
        await service.verify_email_token("esto-no-es-un-jwt")
    assert exc_info.value.status_code == 400


async def test_verify_email_token_user_not_found_raises_404():
    service = build_service()

    with pytest.raises(HTTPException) as exc_info:
        await service.verify_email_token(verification_token(999))
    assert exc_info.value.status_code == 404


# ── Admin: listar / consultar ──────────────────────────────

async def test_get_all_users_paginated():
    repo = FakeUserRepository([make_user(id=i) for i in range(1, 4)])
    service = build_service(user_repo=repo)

    result = await service.get_all_users(page=2, page_size=2)

    assert result.total == 3
    assert len(result.users) == 1


async def test_get_user_by_id_found_and_not_found():
    repo = FakeUserRepository([make_user(id=1)])
    service = build_service(user_repo=repo)

    assert (await service.get_user_by_id(1)).id == 1

    with pytest.raises(HTTPException) as exc_info:
        await service.get_user_by_id(999)
    assert exc_info.value.status_code == 404


async def test_get_pending_users_paginated():
    repo = FakeUserRepository([
        make_user(id=1, status=UserStatus.PENDING),
        make_user(id=2, status=UserStatus.PENDING),
        make_user(id=3, status=UserStatus.ACTIVE),
    ])
    service = build_service(user_repo=repo)

    result = await service.get_pending_users(page=1, page_size=1)

    assert result.total == 2
    assert len(result.users) == 1


# ── Admin: aprobar / cambiar estado ────────────────────────

async def test_approve_user_sets_active_and_notifies(fake_sender):
    repo = FakeUserRepository([make_user(id=1, name="Ana", status=UserStatus.PENDING)])
    service = build_service(user_repo=repo, sender=fake_sender)

    result = await service.approve_user(1)

    assert result["message"] == "Usuario Ana aprobado correctamente"
    user = await repo.get_by_id(1)
    assert user.status == UserStatus.ACTIVE
    assert fake_sender.sent[0]["subject"] == "Tu cuenta ha sido aprobada"


async def test_approve_user_already_active_raises_409():
    repo = FakeUserRepository([make_user(id=1, status=UserStatus.ACTIVE)])
    service = build_service(user_repo=repo)

    with pytest.raises(HTTPException) as exc_info:
        await service.approve_user(1)
    assert exc_info.value.status_code == 409


async def test_approve_user_not_found_raises_404():
    service = build_service()

    with pytest.raises(HTTPException) as exc_info:
        await service.approve_user(999)
    assert exc_info.value.status_code == 404


async def test_change_user_status():
    repo = FakeUserRepository([make_user(id=1, status=UserStatus.ACTIVE)])
    service = build_service(user_repo=repo)

    result = await service.change_user_status(1, UserStatus.BLOCKED)

    assert result["message"] == "Estado del usuario actualizado a 'blocked'"
    assert (await repo.get_by_id(1)).status == UserStatus.BLOCKED


async def test_change_user_status_same_status_raises_409():
    repo = FakeUserRepository([make_user(id=1, status=UserStatus.ACTIVE)])
    service = build_service(user_repo=repo)

    with pytest.raises(HTTPException) as exc_info:
        await service.change_user_status(1, UserStatus.ACTIVE)
    assert exc_info.value.status_code == 409


async def test_change_user_status_not_found_raises_404():
    service = build_service()

    with pytest.raises(HTTPException) as exc_info:
        await service.change_user_status(999, UserStatus.BLOCKED)
    assert exc_info.value.status_code == 404


# ── Admin: actualizar / eliminar / stats ───────────────────

async def test_update_user():
    repo = FakeUserRepository([make_user(id=1, name="Ana")])
    service = build_service(user_repo=repo)

    updated = await service.update_user(1, UserUpdate(name="Ana María"))

    assert updated.name == "Ana María"


async def test_update_user_not_found_raises_404():
    service = build_service()

    with pytest.raises(HTTPException) as exc_info:
        await service.update_user(999, UserUpdate(name="X"))
    assert exc_info.value.status_code == 404


async def test_delete_user():
    repo = FakeUserRepository([make_user(id=1)])
    service = build_service(user_repo=repo)

    result = await service.delete_user(1)

    assert result["message"] == "Usuario 1 eliminado correctamente"
    assert await repo.get_by_id(1) is None


async def test_delete_user_not_found_raises_404():
    service = build_service()

    with pytest.raises(HTTPException) as exc_info:
        await service.delete_user(999)
    assert exc_info.value.status_code == 404


async def test_get_stats():
    repo = FakeUserRepository([
        make_user(id=1, status=UserStatus.ACTIVE),
        make_user(id=2, status=UserStatus.PENDING),
        make_user(id=3, status=UserStatus.PENDING),
    ])
    service = build_service(user_repo=repo)

    stats = await service.get_stats()

    assert stats == {"total_users": 3, "pending_users": 2, "active_users": 1}
