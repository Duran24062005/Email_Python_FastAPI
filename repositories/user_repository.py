from typing import List, Optional

from sqlalchemy.orm import Session

from interfaces.user_interfaces import IUserRepository
from models.user_models import User, UserRole, UserStatus
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
            hash_password=user_data.password,
            role=UserRole.GENERAL,
            status=UserStatus.ACTIVE
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh()

        return User

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Obtiene un usuario que están en pending"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    async def get_pending_users(self) -> Optional[List[User]]:
        """Obtiene un usuario por su ID"""
        return self.db.query(User).filter(User.status.lower() == "PENDING".lower()).all()
    
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
        user = self.db.query(User).filter(User.id == user_id).first()
        if user: 
            self.db.delete(user)
            self.db.commit()
        return False


    async def create_with_hash(self, name: str, email: str, hashed_password: str) -> User:
        """Crea usuario con contraseña ya hasheada"""
        user = User(
            name=name,
            email=email,
            hash_password=hashed_password,
            role=UserRole.GENERAL,
            status=UserStatus.ACTIVE,
            email_verify=False
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    async def update_last_login(self, user_id: int) -> None:
        from datetime import datetime
        user = await self.get_by_id(user_id)
        if user:
            user.last_login = datetime.utcnow()
            self.db.commit()

    async def update_password(self, user_id: int, hashed_password: str) -> None:
        user = await self.get_by_id(user_id)
        if user:
            user.hash_password = hashed_password
            self.db.commit()


    async def count(self) -> int:
        """Cuenta total de usuarios"""
        pass