# PRD: 022 - Envio de Email

**Fecha:** 2026-03-09

## 1. Resumen

Esta funcionalidad permite enviar un email y registrar el resultado del envio en la base de datos. Soporta texto plano, HTML directo o contenido basado en plantilla. El soporte especifico para adjuntos PDF se documenta adicionalmente en `001-pdf-attachments.md`.

## 2. Descripcion de la Funcionalidad

### Endpoint

- **Endpoint:** `POST /emails/send`
- **Tipo de Contenido:** `application/json`

### Parametros

El endpoint acepta los siguientes campos en el body JSON:

- `user_id` (int, requerido): ID del usuario remitente.
- `recipient` (str, requerido): Email del destinatario.
- `subject` (str, requerido): Asunto del correo.
- `body` (str, opcional): Contenido en texto plano.
- `html_body` (str, opcional): Contenido HTML directo.
- `template_name` (str, opcional): Plantilla a renderizar.
- `template_data` (str, opcional): JSON serializado con variables de la plantilla.
- `pdf_attachment` (File, opcional): Archivo PDF adjunto.

### Logica de Implementacion

1.  **Ruta (`routes/email_routes.py`):**
    - Expone `POST /emails/send`.
    - Recibe un body JSON validado con `EmailCreate`.

2.  **Controlador (`controllers/emails_controller.py`):**
    - Recibe un `EmailCreate`.
    - Llama al `EmailService`.
    - Si el resultado queda en estado `failed`, responde `500`.

3.  **Servicio (`services/email_services.py`):**
    - Prepara el contenido HTML con prioridad:
      - `html_body`
      - plantilla renderizada
      - conversion basica desde `body`
    - Crea el registro del email.
    - Intenta enviar el correo y actualiza el estado final.

### Errores Relevantes

- `500`: Falla el envio del email.
- `422`: Fallo de validacion o error en formato de entrada.

## 3. Como Usar

Para enviar un email, se debe realizar una peticion `POST` al endpoint `/emails/send` usando `application/json`.

### Ejemplo con `curl`:

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/emails/send' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "user_id": 3,
    "recipient": "alexisdurangomez588@gmail.com",
    "subject": "Bienvenido",
    "template_name": "welcome.html",
    "template_data": {
      "nombre": "Juan",
      "empresa": "Mi Empresa"
    }
  }'
```

### Uso desde la Documentacion Interactiva de FastAPI

La documentacion en `/docs` muestra este endpoint como body JSON.

## 4. Impacto

- **Capacidad central del sistema:** Permite ejecutar el envio de correos y persistir su trazabilidad.
- **Flexibilidad de contenido:** Acepta distintos modos de composicion del mensaje.
