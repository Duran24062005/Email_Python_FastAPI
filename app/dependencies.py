from fastapi import Depends
from sqlalchemy.orm import Session
from app.config.database.connection import get_db
from app.repositories.email_repository import EmailRepository
from app.repositories.user_repository import UserRepository
from app.services.email_services import EmailService
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.controllers.emails_controller import EmailController
from app.controllers.auth_controller import AuthController
from app.controllers.user_controller import UserController
from app.utils.smtp_email_sender import SMTPEmailSender, MockEmailSender
from app.utils.template_engine import Jinja2TemplateEngine
from app.interfaces.email_interfaces import IEmailSender, ITemplateEngine
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


# ════════════════════════════════════════════════
# FACTORIES DE INFRAESTRUCTURA
# ════════════════════════════════════════════════

def get_email_sender() -> IEmailSender:
    """
    Retorna el sender apropiado según el entorno.
    En producción usa SMTP real, en desarrollo usa Mock.
    """
    env = os.getenv("ENVIRONMENT", "development")

    if env == "production":
        port = int(os.getenv("SMTP_PORT", "587"))
        use_ssl = (port == 465)
        use_tls = (port == 587)
        return SMTPEmailSender(use_tls=use_tls, use_ssl=use_ssl)
    else:
        return MockEmailSender()


def get_template_engine() -> ITemplateEngine:
    return Jinja2TemplateEngine(templates_dir=BASE_DIR / "templates")


# ════════════════════════════════════════════════
# REPOSITORIES
# ════════════════════════════════════════════════

def get_email_repository(db: Session = Depends(get_db)) -> EmailRepository:
    return EmailRepository(db)


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


# ════════════════════════════════════════════════
# SERVICES
# ════════════════════════════════════════════════

def get_email_service(
    repository: EmailRepository = Depends(get_email_repository),
    sender: IEmailSender = Depends(get_email_sender),
    template_engine: ITemplateEngine = Depends(get_template_engine)
) -> EmailService:
    return EmailService(repository, sender, template_engine)


def get_auth_service(
    repository: UserRepository = Depends(get_user_repository),
    sender: IEmailSender = Depends(get_email_sender),
    template_engine: ITemplateEngine = Depends(get_template_engine)
) -> AuthService:
    """AuthService ahora recibe sender para enviar el email de verificación al registrarse"""
    return AuthService(repository, sender, template_engine)


def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository),
    email_repository: EmailRepository = Depends(get_email_repository),
    sender: IEmailSender = Depends(get_email_sender),
    template_engine: ITemplateEngine = Depends(get_template_engine)
) -> UserService:
    return UserService(user_repository, email_repository, sender, template_engine)


# ════════════════════════════════════════════════
# CONTROLLERS
# ════════════════════════════════════════════════

def get_email_controller(
    email_service: EmailService = Depends(get_email_service)
) -> EmailController:
    return EmailController(email_service)


def get_auth_controller(
    auth_service: AuthService = Depends(get_auth_service)
) -> AuthController:
    return AuthController(auth_service)


def get_user_controller(
    user_service: UserService = Depends(get_user_service)
) -> UserController:
    return UserController(user_service)
