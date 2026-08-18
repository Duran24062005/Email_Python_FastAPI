from typing import List, Optional
from datetime import UTC, datetime
from sqlalchemy.orm import Session
from app.interfaces.user_interfaces import IUserRepository
from app.models.user_models import User, UserRole, UserStatus
from app.schemas.user_schemas import UserCreate, UserUpdate


class UserRepository(IUserRepository):
    """
    Implementación del repositorio de usuarios usando SQLAlchemy.
    (Single Responsibility: solo maneja acceso a datos)
    """

    def __init__(self, db: Session):
        self.db = db

    async def create(self, user_data: UserCreate) -> User:
        user = User(
            name=user_data.name,
            email=user_data.email,
            hash_password=user_data.password,
            role=UserRole.GENERAL,
            status=UserStatus.ACTIVE,
            email_verify=False
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

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

    async def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    async def get_by_email(self, user_email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == user_email).first()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        return self.db.query(User).offset(skip).limit(limit).all()

    async def get_pending_users(self) -> List[User]:
        """Retorna todos los usuarios con estado PENDING"""
        return self.db.query(User).filter(
            User.status == UserStatus.PENDING
        ).all()

    async def update(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Actualiza campos de un usuario existente"""
        user = await self.get_by_id(user_id)
        if not user:
            return None

        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        user.updated_at = datetime.now(UTC).replace(tzinfo=None)
        self.db.commit()
        self.db.refresh(user)
        return user

    async def update_status(self, user_id: int, new_status: UserStatus) -> Optional[User]:
        """Actualiza solo el estado de un usuario"""
        user = await self.get_by_id(user_id)
        if not user:
            return None
        user.status = new_status
        user.updated_at = datetime.now(UTC).replace(tzinfo=None)
        self.db.commit()
        self.db.refresh(user)
        return user

    async def update_email_key(self, user_id: int, email_key: str) -> None:
        """Guarda la clave SMTP personal del usuario"""
        user = await self.get_by_id(user_id)
        if user:
            user.email_key = email_key
            user.updated_at = datetime.now(UTC).replace(tzinfo=None)
            self.db.commit()

    async def set_email_verified(self, user_id: int) -> None:
        """Marca el email del usuario como verificado"""
        user = await self.get_by_id(user_id)
        if user:
            user.email_verify = True
            user.updated_at = datetime.now(UTC).replace(tzinfo=None)
            self.db.commit()

    async def update_last_login(self, user_id: int) -> None:
        user = await self.get_by_id(user_id)
        if user:
            user.last_login = datetime.now(UTC).replace(tzinfo=None)
            self.db.commit()

    async def update_password(self, user_id: int, hashed_password: str) -> None:
        user = await self.get_by_id(user_id)
        if user:
            user.hash_password = hashed_password
            user.updated_at = datetime.now(UTC).replace(tzinfo=None)
            self.db.commit()

    async def delete(self, user_id: int) -> bool:
        user = await self.get_by_id(user_id)
        if not user:
            return False
        self.db.delete(user)
        self.db.commit()
        return True

    async def count(self) -> int:
        return self.db.query(User).count()
