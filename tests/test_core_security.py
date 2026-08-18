"""Tests unitarios de app/core/security.py (bcrypt + JWT)."""

from datetime import timedelta

import jwt
import pytest

from app.core import security


# ── hash_password / verify_password ────────────────────────

def test_hash_password_returns_bcrypt_hash():
    hashed = security.hash_password("mi-password-segura")
    assert hashed.startswith("$2")
    assert hashed != "mi-password-segura"


def test_verify_password_round_trip():
    hashed = security.hash_password("mi-password-segura")
    assert security.verify_password("mi-password-segura", hashed) is True


def test_verify_password_wrong_password():
    hashed = security.hash_password("mi-password-segura")
    assert security.verify_password("otra-password", hashed) is False


def test_hash_password_rejects_more_than_72_bytes():
    with pytest.raises(ValueError):
        security.hash_password("a" * 73)


def test_verify_password_returns_false_for_more_than_72_bytes():
    hashed = security.hash_password("mi-password-segura")
    assert security.verify_password("b" * 73, hashed) is False


def test_verify_password_invalid_hash_raises():
    with pytest.raises(ValueError):
        security.verify_password("mi-password", "no-es-un-hash")


# ── create_access_token / decode_access_token ──────────────

def test_create_access_token_round_trip():
    token = security.create_access_token({"sub": "42"})
    payload = security.decode_access_token(token)
    assert payload["sub"] == "42"
    assert "exp" in payload
    assert "iat" in payload


def test_create_access_token_custom_expiration():
    token = security.create_access_token(
        {"sub": "7"}, expires_delta=timedelta(minutes=5)
    )
    payload = security.decode_access_token(token)
    assert payload["sub"] == "7"


def test_decode_access_token_rejects_expired_token():
    token = security.create_access_token(
        {"sub": "1"}, expires_delta=timedelta(seconds=-10)
    )
    with pytest.raises(jwt.ExpiredSignatureError):
        security.decode_access_token(token)


def test_decode_access_token_rejects_invalid_signature():
    token = jwt.encode(
        {"sub": "1", "exp": 9999999999},
        "otra-clave-secreta-con-mas-de-32-bytes-para-hmac",
        algorithm="HS256",
    )
    with pytest.raises(jwt.InvalidTokenError):
        security.decode_access_token(token)


def test_decode_access_token_rejects_garbage():
    with pytest.raises(jwt.InvalidTokenError):
        security.decode_access_token("esto-no-es-un-jwt")
