from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum


class UserStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    UNACTIVE = "deleted"
    BLOCKED = "blocked"


class UserBase(BaseModel):
    """Schema base para usuarios"""
    name: str = Field(..., min_length=1, max_length=255, description="Nombre del usuario")
    email: EmailStr = Field(..., description="Email del usuario")


class UserCreate(UserBase):
    """Schema para crear un usuario"""
    password: str = Field(..., min_length=8, description="Contraseña del usuario")

    @field_validator("password")
    @classmethod
    def validate_password_bcrypt_limit(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("La contraseña no puede exceder 72 bytes.")
        return value

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Juan Pérez",
                "email": "juan@example.com",
                "password": "securepassword123"
            }
        }


class UserUpdate(BaseModel):
    """Schema para actualizar un usuario"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    status: Optional[UserStatus] = None
    email_verify: Optional[bool] = None


class UserResponse(UserBase):
    """Schema para respuesta de usuario"""
    id: int
    status: UserStatus
    email_verify: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserList(BaseModel):
    """Schema para listar usuarios"""
    users: list[UserResponse]
    total: int
    page: int
    page_size: int


# ── Schemas de autenticación ──────────────────────────────

class LoginRequest(BaseModel):
    """Schema para el login"""
    email: EmailStr = Field(..., description="Email del usuario")
    password: str = Field(..., min_length=1, description="Contraseña")

    @field_validator("password")
    @classmethod
    def validate_login_password_bcrypt_limit(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("La contraseña no puede exceder 72 bytes.")
        return value

    class Config:
        json_schema_extra = {
            "example": {
                "email": "juan@example.com",
                "password": "securepassword123"
            }
        }


class TokenResponse(BaseModel):
    """Schema de respuesta del token JWT"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # segundos
    user: UserResponse


class ChangePasswordRequest(BaseModel):
    """Schema para cambiar contraseña"""
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)

    @field_validator("current_password", "new_password")
    @classmethod
    def validate_change_password_bcrypt_limit(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("La contraseña no puede exceder 72 bytes.")
        return value
