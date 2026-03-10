from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.email_model import Email, EmailStatus
from app.schemas.email_schema import EmailCreate, EmailUpdate
from app.interfaces.email_interfaces import IEmailRepository
from datetime import datetime


class EmailRepository(IEmailRepository):
    """
    Repositorio de emails con soporte para consultas por usuario.
    (Single Responsibility: solo maneja acceso a datos)
    """

    def __init__(self, db: Session):
        self.db = db

    async def create(self, email_data: EmailCreate) -> Email:
        email = Email(
            user_id=email_data.user_id,
            recipient=email_data.recipient,
            subject=email_data.subject,
            body=email_data.body,
            html_body=email_data.html_body,
            status=EmailStatus.PENDING
        )
        self.db.add(email)
        self.db.commit()
        self.db.refresh(email)
        return email

    async def get_by_id(self, email_id: int) -> Optional[Email]:
        return self.db.query(Email).filter(Email.id == email_id).first()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Email]:
        return self.db.query(Email).offset(skip).limit(limit).all()

    async def get_by_user_id(
        self, user_id: int, skip: int = 0, limit: int = 10
    ) -> List[Email]:
        """Retorna emails enviados por un usuario específico (bandeja de salida)"""
        return (
            self.db.query(Email)
            .filter(Email.user_id == user_id)
            .order_by(Email.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    async def count_by_user(self, user_id: int) -> int:
        """Cuenta el total de emails de un usuario"""
        return self.db.query(Email).filter(Email.user_id == user_id).count()

    async def update(self, email_id: int, email_data: EmailUpdate) -> Optional[Email]:
        email = await self.get_by_id(email_id)
        if not email:
            return None

        update_data = email_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(email, field, value)

        email.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(email)
        return email

    async def delete(self, email_id: int) -> bool:
        email = await self.get_by_id(email_id)
        if not email:
            return False
        self.db.delete(email)
        self.db.commit()
        return True

    async def count(self) -> int:
        return self.db.query(Email).count()

    async def update_status(
        self,
        email_id: int,
        status: EmailStatus,
        error_message: Optional[str] = None
    ) -> Optional[Email]:
        email = await self.get_by_id(email_id)
        if not email:
            return None

        email.status = status
        email.error_message = error_message

        if status == EmailStatus.SENT:
            email.sent_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(email)
        return email
