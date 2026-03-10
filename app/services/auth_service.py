from datetime import timedelta
from fastapi import HTTPException, status
from app.repositories.user_repository import UserRepository
from app.schemas.user_schemas import UserCreate, UserResponse, LoginRequest, TokenResponse, ChangePasswordRequest
from app.core.security import hash_password, verify_password, create_access_token
from app.core.exceptions import EmailAlreadyExists
from app.models.user_models import UserStatus
from app.interfaces.email_interfaces import IEmailSender, ITemplateEngine
from typing import Optional
from app.config.config import app_config


class AuthService:
    def __init__(
        self,
        repository: UserRepository,
        sender: Optional[IEmailSender] = None,
        template_engine: Optional[ITemplateEngine] = None
    ):
        self.repository = repository
        self.sender = sender
        self.template_engine = template_engine

    async def register(self, user_data: UserCreate) -> UserResponse:
        """Registra un nuevo usuario y envía email de verificación"""
        existing = await self.repository.get_by_email(user_data.email)
        if existing:
            raise EmailAlreadyExists("El email ya está registrado")

        hashed = hash_password(user_data.password)

        user = await self.repository.create_with_hash(
            name=user_data.name,
            email=user_data.email,
            hashed_password=hashed
        )

        # Enviar email de verificación
        await self._send_verification_email(user.id, user.email, user.name)

        return UserResponse.model_validate(user)

    async def _send_verification_email(
        self, user_id: int, email: str, name: str
    ) -> None:
        """
        Genera un token de verificación y lo envía por email.
        El token tiene purpose='email_verification' y expira en 24 horas.
        """
        if not self.sender:
            return  # Sin sender configurado, omitir (modo dev)

        # Token especial para verificación (24 horas)
        verification_token = create_access_token(
            data={"sub": str(user_id), "purpose": "email_verification"},
            expires_delta=timedelta(hours=24)
        )

        verify_url = f"{app_config["DOMAIN"]}api/users/verify-email?token={verification_token}"

        html_body = None
        if self.template_engine:
            try:
                html_body = self.template_engine.render(
                    "welcome_educonnect.html",
                    {
                        "nombre": name,
                        "empresa": "Email FastAPI",
                        "mensaje_adicional": "Por favor verifica tu cuenta haciendo clic en el botón.",
                        "link_accion": verify_url
                    }
                )
            except FileNotFoundError:
                pass

        try:
            await self.sender.send(
                recipient=email,
                subject="Verifica tu cuenta",
                body=f"Hola {name}, verifica tu cuenta en: {verify_url}",
                html_body=html_body
            )
        except Exception as e:
            # No bloquear el registro si el email falla
            print(f"⚠️ No se pudo enviar el email de verificación: {e}")

    async def login(self, credentials: LoginRequest) -> TokenResponse:
        """Autentica un usuario y retorna un JWT"""
        user = await self.repository.get_by_email(credentials.email)

        auth_error = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )

        if not user:
            raise auth_error

        if not verify_password(credentials.password, user.hash_password):
            raise auth_error

        if user.status == UserStatus.BLOCKED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario bloqueado"
            )

        if user.status != UserStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cuenta pendiente de activación"
            )

        await self.repository.update_last_login(user.id)

        token = create_access_token(data={"sub": str(user.id)})

        return TokenResponse(
            access_token=token,
            user=UserResponse.model_validate(user)
        )

    async def change_password(self, user_id: int, data: ChangePasswordRequest) -> dict:
        """Cambia la contraseña del usuario autenticado"""
        user = await self.repository.get_by_id(user_id)

        if not verify_password(data.current_password, user.hash_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña actual es incorrecta"
            )

        new_hash = hash_password(data.new_password)
        await self.repository.update_password(user_id, new_hash)

        return {"message": "Contraseña actualizada correctamente"}
