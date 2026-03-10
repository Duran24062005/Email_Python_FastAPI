from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.config.database.base import Base  # ← Base compartida


class EmailStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # ← "users" no "user"
    recipient = Column(String(255), nullable=False, index=True)
    subject = Column(String(500), nullable=False)
    body = Column(Text, nullable=True)
    html_body = Column(Text, nullable=True)
    status = Column(
        Enum(
            EmailStatus, 
            name='emailstatus', 
            create_type=False,
            values_callable=lambda obj: [e.value for e in obj]
        ),
        default=EmailStatus.PENDING,
        nullable=False
    )
    error_message = Column(Text, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="emails")

    def __repr__(self):
        return f"<Email(id={self.id}, recipient={self.recipient}, status={self.status})>"
