from pydantic import ValidationError

from core.exceptions import EmailAlreadyExists, WeakPassword
from repositories.user_repository import UserRepository
from schemas.user_schemas import UserCreate, UserResponse


# AuthService
# Capa de lógica de negocio (Business Logic Layer)
# Responsabilidad: Implementar reglas de negocio de autenticación
# - Validar datos antes de usar repository
# - Ejecutar lógica de negocio compleja
# - Coordinar entre repositories si es necesario
# - Lanzar errores personalizados
class AuthService:
    """
    Servicio de lógica de negocio para la utenticacion
    (Single Responsibility: orquesta la lógica de negocio)
    (Dependency Inversion: depende de interfaces, no de implementaciones)
    """
    
    def __init__(
            self, 
            respository: UserRepository
        ):
        self.repository = respository

    
    async def register(self, user_data: UserCreate) -> UserResponse:
        """
        Crea un nuevo usuario y guarda el registro en la base de datos
        
        Args:
            user_data: Datos del usuario a crear
            
        Returns:
            UserResponse: Respuesta con el estado del usuario
        """
        # Validaciones de negocio
        if not user_data.name or not user_data.email or not user_data.password:
            raise ValidationError("Campos obligatorios faltantes")

        if len(user_data.password) < 6:
            raise WeakPassword("La contraseña es demasiado corta")

        email_exist = await self.repository.get_by_email(user_data.email)

        if email_exist:
            raise EmailAlreadyExists("El email ya está registrado")

        hashed = hash_password(user_data.password)

        return await self.repository.create(
            UserCreate(
                name=user_data.name,
                email=user_data.email,
                hash_password=hashed
            )
        )