from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.email_model import Email, EmailStatus
from app.schemas.email_schema import EmailCreate, EmailUpdate
from app.interfaces.email_interfaces import IEmailRepository
from datetime import datetime, timezone


class EmailRepository(IEmailRepository):
    """
    Implementación del repositorio de emails usando SQLAlchemy
    (Single Responsibility: solo maneja acceso a datos)
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, email_data: EmailCreate, user_id: int) -> Email:
        """Crea un nuevo registro de email en la base de datos"""
        email = Email(
            user_id=user_id,
            recipient=email_data.recipient,
            subject=email_data.subject,
            body=email_data.body,
            html_body=email_data.html_body,
            status=EmailStatus.PENDING
        )
        
        self.db.add(email)
        await self.db.commit()
        await self.db.refresh(email)
        
        return email
    
    async def get_by_id(self, email_id: int, user_id: Optional[int] = None) -> Optional[Email]:
        """Obtiene un email por su ID, opcionalmente filtrado por user_id"""
        query = select(Email).where(Email.id == email_id)
        if user_id is not None:
            query = query.where(Email.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def get_all(self, skip: int = 0, limit: int = 100, user_id: Optional[int] = None) -> List[Email]:
        """Obtiene lista de emails con paginación, opcionalmente filtrado por user_id"""
        query = select(Email)
        if user_id is not None:
            query = query.where(Email.user_id == user_id)
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update(self, email_id: int, email_data: EmailUpdate, user_id: Optional[int] = None) -> Optional[Email]:
        """Actualiza un email existente, opcionalmente filtrado por user_id"""
        email = await self.get_by_id(email_id, user_id)
        
        if not email:
            return None
        
        update_data = email_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(email, field, value)
        
        email.updated_at = datetime.now(timezone.utc)
        
        await self.db.commit()
        await self.db.refresh(email)
        
        return email
    
    async def delete(self, email_id: int, user_id: Optional[int] = None) -> bool:
        """Elimina un email, opcionalmente filtrado por user_id"""
        email = await self.get_by_id(email_id, user_id)
        
        if not email:
            return False
        
        self.db.delete(email)
        await self.db.commit()
        
        return True
    
    async def count(self, user_id: Optional[int] = None) -> int:
        """Cuenta total de emails, opcionalmente filtrado por user_id"""
        query = select(Email)
        if user_id is not None:
            query = query.where(Email.user_id == user_id)
        result = await self.db.execute(query)
        return len(result.scalars().all())
    
    async def update_status(self, email_id: int, status: EmailStatus, error_message: Optional[str] = None) -> Optional[Email]:
        """Método auxiliar para actualizar el estado de un email"""
        email = await self.get_by_id(email_id)
        
        if not email:
            return None
        
        email.status = status
        email.error_message = error_message
        
        if status == EmailStatus.SENT:
            email.sent_at = datetime.now(timezone.utc)
        
        await self.db.commit()
        await self.db.refresh(email)
        
        return email