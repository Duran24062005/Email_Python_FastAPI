from abc import ABC, abstractmethod
from typing import List, Optional
from models.email_model import Email
from schemas.email_schema import EmailCreate, EmailUpdate


class IEmailRepository(ABC):
    """
    Interface para repositorio de emails (Dependency Inversion Principle)
    Define el contrato que debe cumplir cualquier repositorio de emails
    """
    
    @abstractmethod
    async def create(self, email_data: EmailCreate) -> Email:
        """Crea un nuevo registro de email"""
        pass
    
    @abstractmethod
    async def get_by_id(self, email_id: int) -> Optional[Email]:
        """Obtiene un email por su ID"""
        pass
    
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Email]:
        """Obtiene lista de emails con paginación"""
        pass
    
    @abstractmethod
    async def update(self, email_id: int, email_data: EmailUpdate) -> Optional[Email]:
        """Actualiza un email existente"""
        pass
    
    @abstractmethod
    async def delete(self, email_id: int) -> bool:
        """Elimina un email"""
        pass
    
    @abstractmethod
    async def count(self) -> int:
        """Cuenta total de emails"""
        pass


class IEmailSender(ABC):
    """
    Interface para servicio de envío de emails (Dependency Inversion Principle)
    Permite cambiar el proveedor de email (SMTP, SendGrid, AWS SES, etc.) sin afectar la lógica
    """
    
    @abstractmethod
    async def send(self, recipient: str, subject: str, body: str, html_body: Optional[str] = None) -> bool:
        """
        Envía un email
        
        Returns:
            bool: True si se envió correctamente, False si falló
        """
        pass


class ITemplateEngine(ABC):
    """
    Interface para motor de plantillas (Open/Closed Principle)
    Permite usar diferentes motores de plantillas (Jinja2, Mako, etc.)
    """
    
    @abstractmethod
    def render(self, template_name: str, context: dict) -> str:
        """
        Renderiza una plantilla con el contexto dado
        
        Args:
            template_name: Nombre del archivo de plantilla
            context: Diccionario con datos para la plantilla
            
        Returns:
            str: HTML renderizado
        """
        pass