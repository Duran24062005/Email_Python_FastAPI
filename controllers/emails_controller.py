from typing import Optional
from fastapi import HTTPException, status
from schemas.email_schema import EmailCreate, EmailResponse, EmailUpdate, EmailList
from services.email_services import EmailService


class EmailController:
    """
    Controlador que maneja las peticiones HTTP y coordina con el servicio
    (Single Responsibility: solo maneja la capa de presentación/HTTP)
    """
    
    def __init__(self, email_service: EmailService):
        self.email_service = email_service
    
    async def send_email(self, email_data: EmailCreate) -> EmailResponse:
        """
        Maneja la petición de envío de email
        
        Args:
            email_data: Datos del email a enviar
            
        Returns:
            EmailResponse: Respuesta con el estado del email
            
        Raises:
            HTTPException: Si hay un error al procesar la petición
        """
        try:
            result = await self.email_service.send_email(email_data)
            
            # Si el email falló al enviar, retornar 500
            if result.status == "failed":
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to send email: {result.error_message}"
                )
            
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error: {str(e)}"
            )
    
    async def get_emails(self, page: int = 1, page_size: int = 10) -> EmailList:
        """
        Obtiene lista paginada de emails
        
        Args:
            page: Número de página (default: 1)
            page_size: Cantidad de items por página (default: 10)
            
        Returns:
            EmailList: Lista paginada de emails
        """
        if page < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Page must be greater than 0"
            )
        
        if page_size < 1 or page_size > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Page size must be between 1 and 100"
            )
        
        return await self.email_service.get_all_emails(page, page_size)
    
    async def get_email(self, email_id: int) -> EmailResponse:
        """
        Obtiene un email por su ID
        
        Args:
            email_id: ID del email
            
        Returns:
            EmailResponse: Datos del email
            
        Raises:
            HTTPException: Si el email no existe
        """
        email = await self.email_service.get_email(email_id)
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Email with id {email_id} not found"
            )
        
        return email
    
    async def update_email(self, email_id: int, email_data: EmailUpdate) -> EmailResponse:
        """
        Actualiza un email
        
        Args:
            email_id: ID del email
            email_data: Datos a actualizar
            
        Returns:
            EmailResponse: Email actualizado
            
        Raises:
            HTTPException: Si el email no existe
        """
        email = await self.email_service.update_email(email_id, email_data)
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Email with id {email_id} not found"
            )
        
        return email
    
    async def delete_email(self, email_id: int) -> dict:
        """
        Elimina un email
        
        Args:
            email_id: ID del email
            
        Returns:
            dict: Mensaje de confirmación
            
        Raises:
            HTTPException: Si el email no existe
        """
        success = await self.email_service.delete_email(email_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Email with id {email_id} not found"
            )
        
        return {"message": f"Email {email_id} deleted successfully"}