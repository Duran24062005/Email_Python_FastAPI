from fastapi import APIRouter, Depends, Query
from controllers.emails_controller import EmailController
from schemas.email_schema import EmailCreate, EmailResponse, EmailUpdate, EmailList
from dependencies import get_email_controller

email_router = APIRouter()


@email_router.get("/", status_code=200, response_model=EmailList)
async def get_emails(
    page: int = Query(default=1, ge=1, description="Número de página"),
    page_size: int = Query(default=10, ge=1, le=100, description="Items por página"),
    controller: EmailController = Depends(get_email_controller)
):
    """
    Obtiene lista paginada de emails enviados
    """
    return await controller.get_emails(page, page_size)


@email_router.get("/{email_id}", status_code=200, response_model=EmailResponse)
async def get_email(
    email_id: int,
    controller: EmailController = Depends(get_email_controller)
):
    """
    Obtiene los detalles de un email específico
    """
    return await controller.get_email(email_id)


@email_router.post("/send", status_code=201, response_model=EmailResponse)
async def send_email(
    email: EmailCreate,
    controller: EmailController = Depends(get_email_controller)
):
    """
    Envía un nuevo email
    
    Puedes enviar emails de 3 formas:
    1. Con texto plano: solo proporciona 'body'
    2. Con HTML directo: proporciona 'html_body'
    3. Con plantilla: proporciona 'template_name' y 'template_data'
    """
    return await controller.send_email(email)


@email_router.put("/update/{email_id}", status_code=200, response_model=EmailResponse)
async def update_email(
    email_id: int,
    email: EmailUpdate,
    controller: EmailController = Depends(get_email_controller)
):
    """
    Actualiza el estado de un email
    """
    return await controller.update_email(email_id, email)


@email_router.delete("/{email_id}", status_code=200)
async def delete_email(
    email_id: int,
    controller: EmailController = Depends(get_email_controller)
):
    """
    Elimina un email del registro
    """
    return await controller.delete_email(email_id)