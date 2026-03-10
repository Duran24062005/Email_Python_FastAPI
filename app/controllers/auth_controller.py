from fastapi import HTTPException, status
from app.schemas.user_schemas import UserCreate, LoginRequest, TokenResponse, UserResponse, ChangePasswordRequest
from app.services.auth_service import AuthService
from app.core.exceptions import EmailAlreadyExists, WeakPassword
from app.models.user_models import User


class AuthController:
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service

    async def register(self, user_data: UserCreate) -> UserResponse:
        """
        Mapea excepciones de dominio → HTTPException de FastAPI.
        Las excepciones de Pydantic (validación de schema) las maneja
        FastAPI automáticamente antes de llegar aquí.
        """
        try:
            return await self.auth_service.register(user_data)

        except EmailAlreadyExists as e:
            # Error de negocio → 409 Conflict
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )
        except WeakPassword as e:
            # Error de negocio → 422
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {str(e)}"
            )

    async def login(self, credentials: LoginRequest) -> TokenResponse:
        try:
            return await self.auth_service.login(credentials)

        except HTTPException:
            raise  # Las HTTPException del service se propagan tal cual
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {str(e)}"
            )

    async def me(self, current_user: User) -> UserResponse:
        """El usuario ya viene validado desde la dependency"""
        return UserResponse.model_validate(current_user)

    async def change_password(self, user_id: int, data: ChangePasswordRequest) -> dict:
        try:
            return await self.auth_service.change_password(user_id, data)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno: {str(e)}"
            )
