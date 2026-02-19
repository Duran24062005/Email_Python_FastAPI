

from repositories.user_repository import UserRepository
from schemas.user_schemas import UserCreate, UserResponse


class UserService:
    """
    Servicio de lógica de negocio para users
    (Single Responsibility: orquesta la lógica de negocio)
    (Dependency Inversion: depende de interfaces, no de implementaciones)
    """

    def __init__(
            self, 
            respository: UserRepository
        ):
        self.repository = respository

    
    def create_user(self, user_data: UserCreate) -> UserResponse:
        """
        Crea un nuevo usuario y guarda el registro en la base de datos
        
        Args:
            user_data: Datos del usuario a crear
            
        Returns:
            UserResponse: Respuesta con el estado del usuario
        """
        user_record = UserCreate(
            name=user_data.name,
            email=user_data.email,
            hash_password=user_data.password
        )