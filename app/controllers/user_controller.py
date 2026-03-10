from fastapi import HTTPException, status
from typing import Optional
from app.schemas.user_schemas import UserResponse, UserUpdate, UserList, ChangeStatusRequest
from app.schemas.email_schema import EmailList, EmailResponse, SendWithTemplateRequest
from app.services.user_service import UserService
from app.models.user_models import UserStatus, User


class UserController:
    """
    Controlador de usuarios.
    Mapea peticiones HTTP → UserService.
    Separa errores HTTP de la lógica de negocio.
    """

    def __init__(self, user_service: UserService):
        self.user_service = user_service

    # ─────────────────────────────────────────────
    # USUARIO GENERAL
    # ─────────────────────────────────────────────

    async def get_my_profile(self, current_user: User) -> UserResponse:
        return await self.user_service.get_my_profile(current_user.id)

    async def get_my_inbox(
        self, current_user: User, page: int, page_size: int
    ) -> EmailList:
        return await self.user_service.get_my_inbox(current_user.id, page, page_size)

    async def resend_email(self, current_user: User, email_id: int) -> EmailResponse:
        return await self.user_service.resend_email(current_user.id, email_id)

    async def send_with_template(
        self, current_user: User, data: SendWithTemplateRequest
    ) -> EmailResponse:
        return await self.user_service.send_email_with_template(
            user_id=current_user.id,
            recipient=data.recipient,
            subject=data.subject,
            template_name=data.template_name,
            template_data=data.template_data
        )

    async def save_email_key(self, current_user: User, email_key: str) -> dict:
        return await self.user_service.save_email_key(current_user.id, email_key)

    async def verify_email(self, token: str) -> dict:
        return await self.user_service.verify_email_token(token)

    # ─────────────────────────────────────────────
    # ADMINISTRADOR
    # ─────────────────────────────────────────────

    async def get_all_users(self, page: int, page_size: int) -> UserList:
        if page < 1:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Page debe ser mayor a 0")
        if page_size < 1 or page_size > 100:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Page size debe ser entre 1 y 100")
        return await self.user_service.get_all_users(page, page_size)

    async def get_user_by_id(self, user_id: int) -> UserResponse:
        return await self.user_service.get_user_by_id(user_id)

    async def get_pending_users(self, page: int, page_size: int) -> UserList:
        return await self.user_service.get_pending_users(page, page_size)

    async def approve_user(self, user_id: int) -> dict:
        return await self.user_service.approve_user(user_id)

    async def change_user_status(self, user_id: int, data: ChangeStatusRequest) -> dict:
        return await self.user_service.change_user_status(user_id, data.status)

    async def update_user(self, user_id: int, data: UserUpdate) -> UserResponse:
        return await self.user_service.update_user(user_id, data)

    async def delete_user(self, user_id: int) -> dict:
        return await self.user_service.delete_user(user_id)

    async def get_stats(self) -> dict:
        return await self.user_service.get_stats()
