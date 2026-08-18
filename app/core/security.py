from datetime import UTC, datetime, timedelta
from typing import Optional
import jwt
import bcrypt
import os

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


def hash_password(password: str) -> str:
    """Hashea una contraseña con bcrypt."""
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 72:
        raise ValueError(
            "La contraseña no puede exceder 72 bytes con bcrypt."
        )
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña contra su hash."""
    plain_password_bytes = plain_password.encode("utf-8")
    if len(plain_password_bytes) > 72:
        return False
    return bcrypt.checkpw(
        plain_password_bytes,
        hashed_password.encode("utf-8")
    )


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Genera un JWT con los datos proporcionados"""
    to_encode = data.copy()
    now = datetime.now(UTC).replace(tzinfo=None)  # UTC naive, equivalente a datetime.utcnow()
    expire = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "iat": now})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    Decodifica y valida un JWT.
    Lanza jwt.ExpiredSignatureError o jwt.InvalidTokenError si falla.
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
