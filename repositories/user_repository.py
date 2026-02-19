from typing import List, Optional

from sqlalchemy.orm import Session

from interfaces.user_interfaces import IUserRepository
from models.user_models import User
from schemas.user_schemas import UserCreate, UserUpdate

class UserRepository(IUserRepository):
    """
    Implementación del repositorio de users usando SQLAlchemy
    (Single Responsability: solo maneja acceso a datos)
    """

    def __init__(self, db: Session):
        self.db = db

    async def create(self, user_data: UserCreate) -> User:
        """Crea un nuevo registro de usuario en la base de datos"""
        user = User(
            name=user_data.name,
            email=user_data.email,
            hash_password=user_data.password
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh()

        return User

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Obtiene un usuario por su ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    async def get_by_email(self, user_email: str) -> Optional[User]:
        """Obtiene un usuario por su EMAIL"""
        return self.db.query(User).filter(User.email == user_email).first()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Obtiene lista de usuarios con paginación"""
        return self.db.query(User).offset(skip).limit(limit).all()

    async def update(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Actualiza un usuario existente"""
        pass

    async def delete(self, user_id: int) -> bool:
        """Elimina un usuario"""
        pass

    async def count(self) -> int:
        """Cuenta total de usuarios"""
        pass