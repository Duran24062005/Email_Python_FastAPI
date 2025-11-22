from typing import List, Optional
from sqlalchemy.orm import Session
from models.email_model import Email, EmailStatus
from schemas.email_schema import EmailCreate, EmailUpdate
from interfaces.email_interfaces import IEmailRepository
from datetime import datetime


class EmailRepository(IEmailRepository):
    """
    Implementación del repositorio de emails usando SQLAlchemy
    (Single Responsibility: solo maneja acceso a datos)
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create(self, email_data: EmailCreate) -> Email:
        """Crea un nuevo registro de email en la base de datos"""
        email = Email(
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
        """Obtiene un email por su ID"""
        return self.db.query(Email).filter(Email.id == email_id).first()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Email]:
        """Obtiene lista de emails con paginación"""
        return self.db.query(Email).offset(skip).limit(limit).all()
    
    async def update(self, email_id: int, email_data: EmailUpdate) -> Optional[Email]:
        """Actualiza un email existente"""
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
        """Elimina un email"""
        email = await self.get_by_id(email_id)
        
        if not email:
            return False
        
        self.db.delete(email)
        self.db.commit()
        
        return True
    
    async def count(self) -> int:
        """Cuenta total de emails"""
        return self.db.query(Email).count()
    
    async def update_status(self, email_id: int, status: EmailStatus, error_message: Optional[str] = None) -> Optional[Email]:
        """Método auxiliar para actualizar el estado de un email"""
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