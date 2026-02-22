from fastapi import HTTPException, status
from typing import List, Optional
from repositories.user_repository import UserRepository
from schemas.user_schemas import UserResponse, UserUpdate, UserList
from schemas.email_schema import EmailCreate, EmailResponse, EmailList
from models.user_models import UserStatus
from interfaces.email_interfaces import IEmailSender, ITemplateEngine
from repositories.email_repository import EmailRepository


class UserService:
    """
    Servicio de lógica de negocio para usuarios.
    Cubre funcionalidades de usuario general y administrador.
    Login, registro y cambio de contraseña permanecen en AuthService.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        email_repository: EmailRepository,
        sender: IEmailSender,
        template_engine: Optional[ITemplateEngine] = None
    ):
        self.user_repository = user_repository
        self.email_repository = email_repository
        self.sender = sender
        self.template_engine = template_engine

    # ─────────────────────────────────────────────
    # FUNCIONALIDADES DE USUARIO GENERAL
    # ─────────────────────────────────────────────

    async def get_my_profile(self, user_id: int) -> UserResponse:
        """Retorna el perfil del usuario autenticado."""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        return UserResponse.model_validate(user)

    async def get_my_inbox(self, user_id: int, page: int = 1, page_size: int = 10) -> EmailList:
        """
        Retorna la bandeja de entrada del usuario autenticado
        con todos los emails que ha enviado, paginados.
        """
        skip = (page - 1) * page_size
        emails = await self.email_repository.get_by_user_id(
            user_id=user_id, skip=skip, limit=page_size
        )
        total = await self.email_repository.count_by_user(user_id)

        return EmailList(
            emails=[EmailResponse.model_validate(e) for e in emails],
            total=total,
            page=page,
            page_size=page_size
        )

    async def resend_email(self, user_id: int, email_id: int) -> EmailResponse:
        """
        Reenvía un email existente del usuario.
        Crea un nuevo registro en BD con el mismo contenido.
        """
        original = await self.email_repository.get_by_id(email_id)

        if not original:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email no encontrado"
            )

        if original.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para reenviar este email"
            )

        # Crear nuevo registro para el reenvío
        new_email_data = EmailCreate(
            user_id=user_id,
            recipient=original.recipient,
            subject=original.subject,
            body=original.body,
            html_body=original.html_body
        )
        new_record = await self.email_repository.create(new_email_data)

        # Enviar
        try:
            from models.email_model import EmailStatus
            success = await self.sender.send(
                recipient=original.recipient,
                subject=original.subject,
                body=original.body or "",
                html_body=original.html_body
            )
            final_status = EmailStatus.SENT if success else EmailStatus.FAILED
            await self.email_repository.update_status(new_record.id, final_status)
            new_record.status = final_status
        except Exception as e:
            from models.email_model import EmailStatus
            await self.email_repository.update_status(
                new_record.id, EmailStatus.FAILED, str(e)
            )
            new_record.status = EmailStatus.FAILED
            new_record.error_message = str(e)

        return EmailResponse.model_validate(new_record)

    async def send_email_with_template(
        self,
        user_id: int,
        recipient: str,
        subject: str,
        template_name: str,
        template_data: dict
    ) -> EmailResponse:
        """
        Envía un email usando una plantilla HTML.
        El usuario selecciona la plantilla y proporciona los datos.
        """
        html_body = None
        if self.template_engine:
            try:
                html_body = self.template_engine.render(template_name, template_data)
            except FileNotFoundError:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Plantilla '{template_name}' no encontrada"
                )

        email_data = EmailCreate(
            user_id=user_id,
            recipient=recipient,
            subject=subject,
            body="Por favor visualiza este email en un cliente compatible con HTML.",
            html_body=html_body,
            template_name=template_name,
            template_data=template_data
        )

        record = await self.email_repository.create(email_data)

        try:
            from models.email_model import EmailStatus
            success = await self.sender.send(
                recipient=recipient,
                subject=subject,
                body=email_data.body,
                html_body=html_body
            )
            final_status = EmailStatus.SENT if success else EmailStatus.FAILED
            await self.email_repository.update_status(record.id, final_status)
            record.status = final_status
        except Exception as e:
            from models.email_model import EmailStatus
            await self.email_repository.update_status(
                record.id, EmailStatus.FAILED, str(e)
            )
            record.status = EmailStatus.FAILED
            record.error_message = str(e)

        return EmailResponse.model_validate(record)

    async def save_email_key(self, user_id: int, email_key: str) -> dict:
        """
        Guarda la clave SMTP personal del usuario (email_key).
        Permite al usuario enviar emails desde su propio correo.
        """
        await self.user_repository.update_email_key(user_id, email_key)
        return {"message": "Email key guardada correctamente"}

    async def verify_email_token(self, token: str) -> dict:
        """
        Verifica el token de confirmación enviado al correo del usuario.
        Si es válido, activa email_verify = True en su cuenta.
        """
        from core.security import decode_access_token
        import jwt

        try:
            payload = decode_access_token(token)
            user_id = payload.get("sub")
            purpose = payload.get("purpose")

            if purpose != "email_verification":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Token inválido"
                )

            user = await self.user_repository.get_by_id(int(user_id))
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuario no encontrado"
                )

            if user.email_verify:
                return {"message": "El email ya estaba verificado"}

            await self.user_repository.set_email_verified(int(user_id))
            return {"message": "Email verificado exitosamente"}

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El token de verificación ha expirado"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token inválido"
            )

    # ─────────────────────────────────────────────
    # FUNCIONALIDADES DE ADMINISTRADOR
    # ─────────────────────────────────────────────

    async def get_all_users(self, page: int = 1, page_size: int = 10) -> UserList:
        """Retorna lista paginada de todos los usuarios. Solo admin."""
        skip = (page - 1) * page_size
        users = await self.user_repository.get_all(skip=skip, limit=page_size)
        total = await self.user_repository.count()

        return UserList(
            users=[UserResponse.model_validate(u) for u in users],
            total=total,
            page=page,
            page_size=page_size
        )

    async def get_user_by_id(self, user_id: int) -> UserResponse:
        """Retorna un usuario por ID. Solo admin."""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        return UserResponse.model_validate(user)

    async def get_pending_users(self, page: int = 1, page_size: int = 10) -> UserList:
        """Retorna usuarios con estado PENDING. Solo admin."""
        users = await self.user_repository.get_pending_users()
        # Paginación manual sobre la lista
        start = (page - 1) * page_size
        paginated = users[start: start + page_size] if users else []

        return UserList(
            users=[UserResponse.model_validate(u) for u in paginated],
            total=len(users) if users else 0,
            page=page,
            page_size=page_size
        )

    async def approve_user(self, user_id: int) -> dict:
        """
        Aprueba un usuario cambiando su estado a ACTIVE.
        Solo admin. Envía email de notificación al usuario.
        """
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        if user.status == UserStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El usuario ya está activo"
            )

        await self.user_repository.update_status(user_id, UserStatus.ACTIVE)

        # Notificar al usuario por email
        try:
            html = None
            if self.template_engine:
                try:
                    html = self.template_engine.render(
                        "account_approved.html",
                        {
                            "nombre": user.name,
                            "empresa": "Email FastAPI",
                            "role": user.role.value if user.role else "General",
                            "login_link": "https://tu-dominio.com/login"
                        }
                    )
                except FileNotFoundError:
                    pass

            await self.sender.send(
                recipient=user.email,
                subject="Tu cuenta ha sido aprobada",
                body=f"Hola {user.name}, tu cuenta ha sido aprobada.",
                html_body=html
            )
        except Exception:
            pass  # No fallar si el email no se envía

        return {"message": f"Usuario {user.name} aprobado correctamente"}

    async def change_user_status(self, user_id: int, new_status: UserStatus) -> dict:
        """
        Cambia el estado de un usuario: active, pending, blocked, deleted.
        Solo admin.
        """
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        if user.status == new_status:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El usuario ya tiene el estado '{new_status.value}'"
            )

        await self.user_repository.update_status(user_id, new_status)

        return {
            "message": f"Estado del usuario actualizado a '{new_status.value}'",
            "user_id": user_id
        }

    async def update_user(self, user_id: int, data: UserUpdate) -> UserResponse:
        """Actualiza los datos de un usuario. Solo admin."""
        user = await self.user_repository.update(user_id, data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        return UserResponse.model_validate(user)

    async def delete_user(self, user_id: int) -> dict:
        """Elimina lógicamente un usuario. Solo admin."""
        success = await self.user_repository.delete(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        return {"message": f"Usuario {user_id} eliminado correctamente"}

    async def get_stats(self) -> dict:
        """Retorna estadísticas generales del sistema. Solo admin."""
        total_users = await self.user_repository.count()
        pending_users = await self.user_repository.get_pending_users()

        return {
            "total_users": total_users,
            "pending_users": len(pending_users) if pending_users else 0,
            "active_users": total_users - (len(pending_users) if pending_users else 0),
        }