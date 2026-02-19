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
        if(user_data.name or user_data.email == None or user_data.password == None):
            pass

        email_exist = self.repository.get_by_email(user_data.email)
        user_record = await self.repository.create(
            UserCreate(
                name=user_data.name,
                email=user_data.email,
                hash_password=user_data.password
            )
        )