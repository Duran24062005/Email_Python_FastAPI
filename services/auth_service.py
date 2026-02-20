from fastapi import HTTPException, status
from repositories.user_repository import UserRepository
from schemas.user_schemas import UserCreate, UserResponse, LoginRequest, TokenResponse, ChangePasswordRequest
from core.security import hash_password, verify_password, create_access_token
from core.exceptions import EmailAlreadyExists, WeakPassword
from models.user_models import UserStatus


class AuthService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def register(self, user_data: UserCreate) -> UserResponse:
        """Registra un nuevo usuario"""
        # Verificar email duplicado
        existing = await self.repository.get_by_email(user_data.email)
        if existing:
            raise EmailAlreadyExists("El email ya está registrado")

        # Hashear contraseña antes de guardar
        hashed = hash_password(user_data.password)

        user = await self.repository.create_with_hash(
            name=user_data.name,
            email=user_data.email,
            hashed_password=hashed
        )

        return UserResponse.model_validate(user)

    async def login(self, credentials: LoginRequest) -> TokenResponse:
        """Autentica un usuario y retorna un JWT"""
        user = await self.repository.get_by_email(credentials.email)

        # Mismo mensaje para email y contraseña incorrectos (seguridad)
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

        # Actualizar last_login
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