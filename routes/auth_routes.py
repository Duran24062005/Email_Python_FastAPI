from fastapi import APIRouter, Depends
from controllers.auth_controller import AuthController
from schemas.user_schemas import UserCreate, LoginRequest, TokenResponse, UserResponse, ChangePasswordRequest
from middlewares.auth_middleware import get_current_active_user
from models.user_models import User
from dependencies import get_auth_controller  # lo agregas en dependencies.py

auth_router = APIRouter()


@auth_router.post("/register", status_code=201, response_model=UserResponse)
async def register(
    user_data: UserCreate,
    controller: AuthController = Depends(get_auth_controller)
):
    """
    Registrar un nuevo usuario.

    Valida unicidad de email, hashea la contraseña y crea el registro.

    ⚠️ El email debe ser único en el sistema.
    """
    return await controller.register(user_data)


@auth_router.post("/login", status_code=200, response_model=TokenResponse)
async def login(
    credentials: LoginRequest,
    controller: AuthController = Depends(get_auth_controller)
):
    """
    Autenticar usuario y obtener token JWT.

    Retorna un Bearer token válido por 30 minutos.

    ⚠️ La cuenta debe estar en estado ACTIVE.
    """
    return await controller.login(credentials)

@auth_router.post("/logout", status_code=200, response_model=TokenResponse)
async def logout(
    credentials: LoginRequest,
    controller: AuthController = Depends(get_auth_controller)
):
    """
    Qitar la autenticación al usuario.

    Recibe un Bearer token válido.

    ⚠️ Se debe eliminar el token en en frontend tambien.
    """
    return await controller.login(credentials)


@auth_router.get("/me", status_code=200, response_model=UserResponse)
async def me(
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtener perfil del usuario autenticado.

    🔒 Requiere Bearer token válido en el header Authorization.
    """
    return UserResponse.model_validate(current_user)


@auth_router.post("/change-password", status_code=200)
async def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    controller: AuthController = Depends(get_auth_controller)
):
    """
    Cambiar contraseña del usuario autenticado.

    🔒 Requiere Bearer token válido.

    ⚠️ Debes enviar tu contraseña actual para confirmar.
    """
    return await controller.change_password(current_user.id, data)