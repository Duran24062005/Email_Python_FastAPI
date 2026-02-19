from sqlalchemy import Column, Integer, String, DateTime, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class UserStatus(str, enum.Enum):
    """Estados posibles de un email"""
    PENDING = "pending"
    ACTIVE = "active"
    UNACTIVE = "deleted"
    BLOCKED = "blocked"

class UserRole(str, enum.Enum):
    """Estados posibles de un email"""
    ADMIN = "admin"
    GENERAL = "general"


class User(Base):
    """Modelo de base de datos para usuarios"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True, unique=True)
    hash_password = Column(Integer, nullable=False)
    email_key = Column(String(255), nullable=True, index=True)
    status = Column(
        Enum(UserStatus, name='userStatus', create_type=False),
        default=UserStatus.ACTIVE,
        nullable=False
    )
    role = Column(
        Enum(UserRole, name='userRole', create_type=False),
        default=UserRole.GENERAL,
        nullable=False
    )
    last_login = Column(DateTime, nullable=True)
    email_verify = Column(Boolean, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relacion hacia inversa
    email = relationship("Emails", back_populates="user", uselist=False)