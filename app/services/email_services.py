from typing import List, Optional
from app.schemas.email_schema import EmailCreate, EmailResponse, EmailUpdate, EmailList
from app.interfaces.email_interfaces import IEmailRepository, IEmailSender, ITemplateEngine
from app.models.email_model import EmailStatus, Email


class EmailService:
    """
    Servicio de lógica de negocio para emails
    (Single Responsibility: orquesta la lógica de negocio)
    (Dependency Inversion: depende de interfaces, no de implementaciones)
    """
    
    def __init__(
        self,
        repository: IEmailRepository,
        sender: IEmailSender,
        template_engine: Optional[ITemplateEngine] = None
    ):
        self.repository = repository
        self.sender = sender
        self.template_engine = template_engine
    
    async def send_email(self, email_data: EmailCreate, user_id: int) -> EmailResponse:
        """
        Envía un email y guarda el registro en la base de datos
        
        Args:
            email_data: Datos del email a enviar
            user_id: ID del usuario que envía el email
            
        Returns:
            EmailResponse: Respuesta con el estado del email
        """
        # 1. Preparar el contenido del email
        html_body = await self._prepare_email_content(email_data)
        body = email_data.body or "Por favor, visualiza este email en un cliente compatible con HTML."
        
        # 2. Crear registro en la base de datos
        email_record = await self.repository.create(
            EmailCreate(
                recipient=email_data.recipient,
                subject=email_data.subject,
                body=body,
                html_body=html_body
            ),
            user_id=user_id
        )
        
        # 3. Intentar enviar el email
        try:
            success = await self.sender.send(
                recipient=email_data.recipient,
                subject=email_data.subject,
                body=body,
                html_body=html_body
            )
            
            # 4. Actualizar estado según resultado
            if success:
                await self.repository.update_status(email_record.id, EmailStatus.SENT)
                email_record.status = EmailStatus.SENT
            else:
                await self.repository.update_status(
                    email_record.id,
                    EmailStatus.FAILED,
                    "Failed to send email"
                )
                email_record.status = EmailStatus.FAILED
                
        except Exception as e:
            # Manejar errores de envío
            await self.repository.update_status(
                email_record.id,
                EmailStatus.FAILED,
                str(e)
            )
            email_record.status = EmailStatus.FAILED
            email_record.error_message = str(e)
        
        return EmailResponse.model_validate(email_record)
    
    async def _prepare_email_content(self, email_data: EmailCreate) -> str:
        """
        Prepara el contenido HTML del email
        
        Returns:
            str: Contenido HTML del email
        """
        # Si se proporciona HTML directamente
        if email_data.html_body:
            return email_data.html_body
        
        # Si se especifica una plantilla y hay motor de plantillas
        if email_data.template_name and self.template_engine:
            try:
                return self.template_engine.render(
                    email_data.template_name,
                    email_data.template_data or {}
                )
            except FileNotFoundError:
                # Si la plantilla no existe, usar el body como fallback
                return f"<html><body>{email_data.body or ''}</body></html>"
        

        # Fallback: convertir texto plano a HTML básico
        if email_data.body:
            return f"<html><body><p>{email_data.body}</p></body></html>"
        
        return "<html><body></body></html>"
    
    async def get_email(self, email_id: int, user_id: int) -> Optional[EmailResponse]:
        """Obtiene un email por su ID, filtrado por user_id"""
        email = await self.repository.get_by_id(email_id, user_id)
        
        if not email:
            return None
        
        return EmailResponse.model_validate(email)
    
    async def get_all_emails(self, page: int = 1, page_size: int = 10, user_id: int = None) -> EmailList:
        """
        Obtiene lista paginada de emails, filtrado por user_id
        
        Args:
            page: Número de página (inicia en 1)
            page_size: Cantidad de items por página
            user_id: ID del usuario para filtrar emails
            
        Returns:
            EmailList: Lista paginada de emails
        """
        skip = (page - 1) * page_size
        
        emails = await self.repository.get_all(skip=skip, limit=page_size, user_id=user_id)
        total = await self.repository.count(user_id=user_id)
        
        return EmailList(
            emails=[EmailResponse.model_validate(email) for email in emails],
            total=total,
            page=page,
            page_size=page_size
        )
    
    async def update_email(self, email_id: int, email_data: EmailUpdate, user_id: int) -> Optional[EmailResponse]:
        """Actualiza un email, filtrado por user_id"""
        email = await self.repository.update(email_id, email_data, user_id)
        
        if not email:
            return None
        
        return EmailResponse.model_validate(email)
    
    async def delete_email(self, email_id: int, user_id: int) -> bool:
        """Elimina un email, filtrado por user_id"""
        return await self.repository.delete(email_id, user_id)

