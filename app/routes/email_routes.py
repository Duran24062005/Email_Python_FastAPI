from fastapi import APIRouter, Depends, Query, File, UploadFile, Form, HTTPException, status
from app.controllers.emails_controller import EmailController
from app.schemas.email_schema import EmailCreate, EmailResponse, EmailUpdate, EmailList
from app.dependencies import get_email_controller
from typing import Optional
import json

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
    Envía un nuevo email usando `application/json`.

    Puedes enviar emails de 3 formas:
    1. Con texto plano: solo proporciona `body`
    2. Con HTML directo: proporciona `html_body`
    3. Con plantilla: proporciona `template_name` y `template_data`
    """
    return await controller.send_email(email_data=email, attachment=None)


@email_router.post("/send/form", status_code=201, response_model=EmailResponse)
async def send_email_form(
    user_id: int = Form(...),
    recipient: str = Form(...),
    subject: str = Form(...),
    body: Optional[str] = Form(None),
    html_body: Optional[str] = Form(None),
    template_name: Optional[str] = Form(None),
    template_data: Optional[str] = Form(None),
    pdf_attachment: Optional[UploadFile] = File(None),
    controller: EmailController = Depends(get_email_controller)
):
    """
    Envía un nuevo email usando `multipart/form-data`.

    Puedes enviar emails de 3 formas:
    1. Con texto plano: solo proporciona `body`
    2. Con HTML directo: proporciona `html_body`
    3. Con plantilla: proporciona `template_name` y `template_data` como string JSON

    Usa este endpoint cuando necesites adjuntar un PDF.
    """
    try:
        template_data_dict = json.loads(template_data) if template_data else None
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"template_data must be valid JSON: {exc.msg}"
        ) from exc

    email = EmailCreate(
        user_id=user_id,
        recipient=recipient,
        subject=subject,
        body=body,
        html_body=html_body,
        template_name=template_name,
        template_data=template_data_dict
    )

    return await controller.send_email(
        email_data=email,
        attachment=pdf_attachment
    )


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
