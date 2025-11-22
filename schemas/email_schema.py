from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from datetime import datetime


class EmailBase(BaseModel):
    """Schema base para emails"""
    recipient: EmailStr = Field(..., description="Email del destinatario")
    subject: str = Field(..., min_length=1, max_length=200, description="Asunto del email")


class EmailCreate(EmailBase):
    """Schema para crear un email (envío directo)"""
    body: Optional[str] = Field(None, description="Cuerpo del email en texto plano")
    html_body: Optional[str] = Field(None, description="Cuerpo del email en HTML")
    template_name: Optional[str] = Field(None, description="Nombre de la plantilla a usar")
    template_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Datos para la plantilla")

    class Config:
        json_schema_extra = {
            "example": {
                "recipient": "usuario@example.com",
                "subject": "Bienvenido a nuestra plataforma",
                "template_name": "welcome",
                "template_data": {
                    "nombre": "Juan Pérez",
                    "empresa": "Mi Empresa"
                }
            }
        }


class EmailResponse(EmailBase):
    """Schema para respuesta de email"""
    id: int
    status: str = Field(..., description="Estado del email: sent, failed, pending")
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


class EmailUpdate(BaseModel):
    """Schema para actualizar un email"""
    status: Optional[str] = None
    error_message: Optional[str] = None


class EmailList(BaseModel):
    """Schema para listar emails"""
    emails: list[EmailResponse]
    total: int
    page: int
    page_size: int