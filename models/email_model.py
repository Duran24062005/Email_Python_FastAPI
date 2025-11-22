from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class EmailStatus(str, enum.Enum):
    """Estados posibles de un email"""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class Email(Base):
    """Modelo de base de datos para emails"""
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    recipient = Column(String(255), nullable=False, index=True)
    subject = Column(String(500), nullable=False)
    body = Column(Text, nullable=True)
    html_body = Column(Text, nullable=True)
    status = Column(
        Enum(EmailStatus, name='emailstatus', create_type=False), 
        default=EmailStatus.PENDING, 
        nullable=False
    )
    error_message = Column(Text, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Email(id={self.id}, recipient={self.recipient}, status={self.status})>"