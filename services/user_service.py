from fastapi import HTTPException, status

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

    async def get_all_users():
        """
        Obtiene una lista de usuarios
        """



    async def get_user_by_id(self, user_id: int):
        """
        Obtenine un usuario por su id

        Args: ID del usuario a buscar

        Return: Retorna el al usuario o 
        """
        user = await self.repository.get_by_id(user_id)

        error = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

        if not user:
            raise error
        
        return user
    
    async def get_user_by_email(self, user_email: int):
        """
        Obtenine un usuario por su Email

        Args: Email del usuario a buscar

        Return: Retorna el al usuario o Un error en caso de no encontrarlo
        """
        user = await self.repository.get_by_email(user_email)

        error = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

        if not user:
            raise error
        
        return user
    
    async def update_user_state():
        pass

    async def verify_email():
        pass

    async def 