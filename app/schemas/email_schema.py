from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class EmailStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class EmailBase(BaseModel):
    recipient: EmailStr = Field(..., description="Email del destinatario")
    subject: str = Field(..., min_length=1, max_length=500, description="Asunto del email")


class EmailCreate(EmailBase):
    user_id: int = Field(..., description="ID del usuario que envía el email")
    body: Optional[str] = Field(None, description="Cuerpo en texto plano")
    html_body: Optional[str] = Field(None, description="Cuerpo en HTML")
    template_name: Optional[str] = Field(None, description="Nombre de la plantilla")
    template_data: Optional[Dict[str, Any]] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "recipient": "usuario@example.com",
                "subject": "Bienvenido",
                "template_name": "welcome.html",
                "template_data": {
                    "nombre": "Juan",
                    "empresa": "Mi Empresa"
                }
            }
        }


class EmailResponse(EmailBase):
    id: int
    user_id: int
    body: Optional[str] = None
    html_body: Optional[str] = None
    status: EmailStatus
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EmailUpdate(BaseModel):
    status: Optional[EmailStatus] = None
    error_message: Optional[str] = None
    sent_at: Optional[datetime] = None


class EmailList(BaseModel):
    emails: list[EmailResponse]
    total: int
    page: int
    page_size: int


# ── Schema específico para envío con plantilla desde rutas de usuario ──

class SendWithTemplateRequest(BaseModel):
    """Envío de email con plantilla HTML seleccionada por el usuario"""
    recipient: EmailStr = Field(..., description="Email del destinatario")
    subject: str = Field(..., min_length=1, max_length=500)
    template_name: str = Field(..., description="Nombre de la plantilla (ej: welcome.html)")
    template_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Variables para inyectar en la plantilla"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "recipient": "cliente@example.com",
                "subject": "Bienvenido a nuestra plataforma",
                "template_name": "welcome.html",
                "template_data": {
                    "nombre": "Juan Pérez",
                    "empresa": "Mi Empresa",
                    "mensaje_adicional": "Gracias por registrarte"
                }
            }
        }