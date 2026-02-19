from abc import ABC, abstractmethod
from typing import List, Optional
from models.user_models import User
from schemas.user_schemas import UserCreate, UserUpdate

class IUserRepository(ABC):
    """
    Interface para repositorio de users (Dependency Inversion Principle)
    Define el contrato que debe cumplir cualquier repositorio de users
    """

    @abstractmethod
    async def create(self, userData: UserCreate) -> User:
        """Crea un nuevo registro de usuario"""
        pass

    @abstractmethod
    async def get_by_id(self, user_id: int) -> User:
        """Obtiene un usuario por su ID"""
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Obtiene lista de usuarios con paginación"""
        pass

    @abstractmethod
    async def update(self, user_id: int, userData: UserUpdate) -> Optional[User]:
        """Actualiza un usuario existente"""
        pass

    @abstractmethod
    async def delete(self, user_id: int) -> bool:
        """Elimina un usuario"""
        pass

    @abstractmethod
    async def count(self) -> int:
        """Cuenta total de usuarios"""
        pass