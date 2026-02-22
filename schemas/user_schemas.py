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
    name: str = Field(..., min_length=1, max_length=255, description="Nombre del usuario")
    email: EmailStr = Field(..., description="Email del usuario")


class UserCreate(UserBase):
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
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    status: Optional[UserStatus] = None
    email_verify: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    status: UserStatus
    email_verify: Optional[bool] = None
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserList(BaseModel):
    users: list[UserResponse]
    total: int
    page: int
    page_size: int


# ── Auth schemas ──────────────────────────────────────────

class LoginRequest(BaseModel):
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
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 1800
    user: UserResponse


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)

    @field_validator("current_password", "new_password")
    @classmethod
    def validate_change_password_bcrypt_limit(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("La contraseña no puede exceder 72 bytes.")
        return value


# ── Admin / User management schemas ──────────────────────

class ChangeStatusRequest(BaseModel):
    """Schema para cambiar el estado de un usuario (admin)"""
    status: UserStatus = Field(..., description="Nuevo estado del usuario")

    class Config:
        json_schema_extra = {
            "example": {"status": "blocked"}
        }


class SaveEmailKeyRequest(BaseModel):
    """Schema para guardar la clave SMTP personal del usuario"""
    email_key: str = Field(
        ..., min_length=1,
        description="Contraseña de aplicación SMTP del usuario"
    )

    class Config:
        json_schema_extra = {
            "example": {"email_key": "xxxx xxxx xxxx xxxx"}
        }
