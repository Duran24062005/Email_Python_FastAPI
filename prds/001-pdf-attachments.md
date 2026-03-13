# PRD: 001 - Soporte para Archivos Adjuntos en PDF

**Fecha:** 2024-07-25

## 1. Resumen

Esta funcionalidad permite a los usuarios adjuntar archivos PDF a los correos electrónicos enviados a través de la API. El soporte de adjuntos se expone mediante un endpoint dedicado `multipart/form-data`, evitando afectar el endpoint JSON principal.

## 2. Descripción de la Funcionalidad

### Endpoint Modificado

- **Endpoint:** `POST /emails/send/form`
- **Tipo de Contenido:** `multipart/form-data`

### Parámetros

El endpoint acepta los siguientes campos como parte de un formulario `multipart/form-data`:

- `user_id` (int, requerido): ID del usuario que envía el correo.
- `recipient` (str, requerido): Email del destinatario.
- `subject` (str, requerido): Asunto del correo.
- `body` (str, opcional): Cuerpo del correo en texto plano.
- `html_body` (str, opcional): Cuerpo del correo en formato HTML.
- `template_name` (str, opcional): Nombre de la plantilla a utilizar.
- `template_data` (str, opcional): Un string en formato JSON con los datos para la plantilla.
- `pdf_attachment` (File, opcional): El archivo PDF a adjuntar.

### Lógica de Implementación

1.  **Ruta (`routes/email_routes.py`):**
    - Se modificó la firma de la función `send_email` para aceptar `Form` y `File`.
    - `template_data` se recibe como un string JSON y se decodifica en el controlador.

2.  **Controlador (`controllers/emails_controller.py`):**
    - El método `send_email` se actualizó para recibir los nuevos parámetros de la ruta.
    - Se pasa el archivo adjunto al `EmailService`.

3.  **Servicio (`services/email_services.py`):**
    - El método `send_email` lee el contenido del archivo (`UploadFile`) y lo pasa al `IEmailSender`.

4.  **Sender (`utils/smtp_email_sender.py`):**
    - La clase `SMTPEmailSender` ahora construye un mensaje `MIMEMultipart`.
    - El contenido del correo (texto y HTML) se adjunta como una parte.
    - Si se proporciona un archivo adjunto, se crea una `MIMEApplication` y se adjunta al mensaje.

## 3. Cómo Usar

Para enviar un correo con un archivo PDF adjunto, se debe realizar una petición `POST` al endpoint `/emails/send/form` utilizando `multipart/form-data`.

### Ejemplo con `curl`:

```bash
curl -X 'POST' 
  'http://127.0.0.1:8000/emails/send/form' 
  -H 'accept: application/json' 
  -H 'Content-Type: multipart/form-data' 
  -F 'user_id=1' 
  -F 'recipient=destinatario@example.com' 
  -F 'subject=Asunto del Correo con Adjunto' 
  -F 'body=Este es el cuerpo del correo.' 
  -F 'pdf_attachment=@/ruta/a/tu/archivo.pdf;type=application/pdf'
```

### Uso desde la Documentación Interactiva de FastAPI

La documentación en `/docs` ahora muestra una interfaz para cargar el archivo directamente desde el navegador, junto con los demás campos del formulario.

## 4. Impacto

- **Flexibilidad:** Los usuarios ahora pueden enviar documentos importantes como facturas, reportes o cualquier otro material en formato PDF.
- **Separacion de Contratos:** El soporte PDF vive en `/emails/send/form`, mientras que `/emails/send` mantiene `application/json` para integraciones simples.
