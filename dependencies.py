from fastapi import Depends
from sqlalchemy.orm import Session
from config.database.connection import get_db
from repositories.email_repository import EmailRepository
from services.email_services import EmailService
from controllers.emails_controller import EmailController
from utils.smtp_email_sender import SMTPEmailSender, MockEmailSender
from utils.template_engine import Jinja2TemplateEngine
from interfaces.email_interfaces import IEmailSender, ITemplateEngine
import os


# ============================================
# CONFIGURACIÓN DE DEPENDENCIAS
# ============================================

def get_email_sender() -> IEmailSender:
    """
    Factory para obtener el sender de emails apropiado
    (Dependency Inversion: retorna interface, no implementación concreta)
    """
    # En producción usa SMTP real, en desarrollo usa Mock
    env = os.getenv("ENVIRONMENT", "development")
    
    if env == "production":
        port = int(os.getenv("SMTP_PORT", "587"))
        # Puerto 465 requiere SSL, puerto 587 requiere TLS
        use_ssl = (port == 465)
        use_tls = (port == 587)
        
        return SMTPEmailSender(
            use_tls=use_tls,
            use_ssl=use_ssl
        )
    else:
        return MockEmailSender()


def get_template_engine() -> ITemplateEngine:
    """
    Factory para obtener el motor de plantillas
    """
    
    return Jinja2TemplateEngine(templates_dir="templates")


# ============================================
# DEPENDENCIAS PARA FASTAPI
# ============================================

def get_email_repository(db: Session = Depends(get_db)) -> EmailRepository:
    """Dependency para obtener el repositorio de emails"""
    return EmailRepository(db)


def get_email_service(
    repository: EmailRepository = Depends(get_email_repository),
    sender: IEmailSender = Depends(get_email_sender),
    template_engine: ITemplateEngine = Depends(get_template_engine)
) -> EmailService:
    """
    Dependency para obtener el servicio de emails
    (Inyección de dependencias completa)
    """
    return EmailService(repository, sender, template_engine)


def get_email_controller(
    email_service: EmailService = Depends(get_email_service)
) -> EmailController:
    """Dependency para obtener el controlador de emails"""
    return EmailController(email_service)