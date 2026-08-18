"""Tests unitarios de los schemas Pydantic (validación)."""

import pytest
from pydantic import ValidationError

from app.schemas.user_schemas import (
    UserCreate,
    UserUpdate,
    LoginRequest,
    ChangePasswordRequest,
    ChangeStatusRequest,
    SaveEmailKeyRequest,
    UserStatus,
)
from app.schemas.email_schema import EmailCreate, EmailUpdate, SendWithTemplateRequest


# ── UserCreate ─────────────────────────────────────────────

def test_user_create_valid():
    user = UserCreate(name="Juan", email="juan@example.com", password="securepass123")
    assert user.name == "Juan"
    assert user.email == "juan@example.com"


def test_user_create_rejects_short_password():
    with pytest.raises(ValidationError):
        UserCreate(name="Juan", email="juan@example.com", password="short")


def test_user_create_rejects_password_over_72_bytes():
    with pytest.raises(ValidationError):
        UserCreate(name="Juan", email="juan@example.com", password="a" * 73)


def test_user_create_rejects_invalid_email():
    with pytest.raises(ValidationError):
        UserCreate(name="Juan", email="no-es-un-email", password="securepass123")


def test_user_create_rejects_empty_name():
    with pytest.raises(ValidationError):
        UserCreate(name="", email="juan@example.com", password="securepass123")


# ── UserUpdate ─────────────────────────────────────────────

def test_user_update_partial():
    update = UserUpdate(name="Nuevo Nombre")
    dumped = update.model_dump(exclude_unset=True)
    assert dumped == {"name": "Nuevo Nombre"}


def test_user_update_with_status():
    update = UserUpdate(status=UserStatus.BLOCKED)
    assert update.model_dump(exclude_unset=True) == {"status": UserStatus.BLOCKED}


def test_user_update_rejects_invalid_email():
    with pytest.raises(ValidationError):
        UserUpdate(email="no-valido")


# ── LoginRequest ───────────────────────────────────────────

def test_login_request_valid():
    login = LoginRequest(email="juan@example.com", password="securepass123")
    assert login.email == "juan@example.com"


def test_login_request_rejects_invalid_email():
    with pytest.raises(ValidationError):
        LoginRequest(email="mal", password="securepass123")


def test_login_request_rejects_password_over_72_bytes():
    with pytest.raises(ValidationError):
        LoginRequest(email="juan@example.com", password="a" * 73)


# ── ChangePasswordRequest ──────────────────────────────────

def test_change_password_valid():
    data = ChangePasswordRequest(
        current_password="vieja-pass", new_password="nueva-pass-segura"
    )
    assert data.new_password == "nueva-pass-segura"


def test_change_password_rejects_short_new_password():
    with pytest.raises(ValidationError):
        ChangePasswordRequest(current_password="vieja-pass", new_password="corta")


def test_change_password_rejects_over_72_bytes():
    with pytest.raises(ValidationError):
        ChangePasswordRequest(current_password="vieja-pass", new_password="a" * 73)


# ── EmailCreate / EmailUpdate ──────────────────────────────

def test_email_create_valid_with_template():
    email = EmailCreate(
        user_id=1,
        recipient="destino@example.com",
        subject="Bienvenido",
        template_name="welcome.html",
        template_data={"nombre": "Ana"},
    )
    assert email.template_data == {"nombre": "Ana"}
    assert email.body is None


def test_email_create_rejects_invalid_recipient():
    with pytest.raises(ValidationError):
        EmailCreate(user_id=1, recipient="mal", subject="Asunto")


def test_email_create_rejects_empty_subject():
    with pytest.raises(ValidationError):
        EmailCreate(user_id=1, recipient="destino@example.com", subject="")


def test_email_update_partial():
    update = EmailUpdate(status="sent")
    assert update.model_dump(exclude_unset=True) == {"status": "sent"}


# ── SendWithTemplateRequest ────────────────────────────────

def test_send_with_template_valid():
    data = SendWithTemplateRequest(
        recipient="cliente@example.com",
        subject="Oferta",
        template_name="welcome.html",
        template_data={"nombre": "Ana"},
    )
    assert data.template_name == "welcome.html"


# ── Admin schemas ──────────────────────────────────────────

def test_change_status_request_valid():
    data = ChangeStatusRequest(status=UserStatus.BLOCKED)
    assert data.status == UserStatus.BLOCKED


def test_save_email_key_rejects_empty():
    with pytest.raises(ValidationError):
        SaveEmailKeyRequest(email_key="")


def test_save_email_key_valid():
    data = SaveEmailKeyRequest(email_key="xxxx xxxx xxxx xxxx")
    assert data.email_key == "xxxx xxxx xxxx xxxx"
