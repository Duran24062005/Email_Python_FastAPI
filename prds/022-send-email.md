# PRD: 022 - Envio de Email

**Fecha:** 2026-03-09

## 1. Resumen

Esta funcionalidad permite enviar un email y registrar el resultado del envio en la base de datos. Soporta texto plano, HTML directo o contenido basado en plantilla. El soporte especifico para adjuntos PDF se documenta adicionalmente en `001-pdf-attachments.md`.

## 2. Descripcion de la Funcionalidad

### Endpoint

- **Endpoint:** `POST /emails/send`
- **Tipo de Contenido:** `multipart/form-data`

### Parametros

El endpoint acepta los siguientes campos:

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
    - Recibe datos como `Form` y `File`.
    - Convierte `template_data` desde string JSON a diccionario.

2.  **Controlador (`controllers/emails_controller.py`):**
    - Construye un `EmailCreate`.
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

Para enviar un email, se debe realizar una peticion `POST` al endpoint `/emails/send` usando `multipart/form-data`.

### Ejemplo con `curl`:

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/emails/send' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'user_id=1' \
  -F 'recipient=destinatario@example.com' \
  -F 'subject=Asunto del correo' \
  -F 'body=Texto del mensaje'
```

### Uso desde la Documentacion Interactiva de FastAPI

La documentacion en `/docs` muestra este endpoint como formulario multiparte, permitiendo cargar datos de texto y archivos.

## 4. Impacto

- **Capacidad central del sistema:** Permite ejecutar el envio de correos y persistir su trazabilidad.
- **Flexibilidad de contenido:** Acepta distintos modos de composicion del mensaje.
