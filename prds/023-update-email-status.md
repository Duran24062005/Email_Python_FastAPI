# PRD: 023 - Actualizacion de Registro de Email

**Fecha:** 2026-03-09

## 1. Resumen

Esta funcionalidad permite actualizar manualmente el estado y metadatos de un email existente en la base de datos.

## 2. Descripcion de la Funcionalidad

### Endpoint

- **Endpoint:** `PUT /emails/update/{email_id}`
- **Tipo de Contenido:** `application/json`

### Parametros

El endpoint acepta:

- `email_id` (int, requerido): ID del email a actualizar.
- Body `EmailUpdate` con campos opcionales:
  - `status`
  - `error_message`
  - `sent_at`

### Logica de Implementacion

1.  **Ruta (`routes/email_routes.py`):**
    - Expone `PUT /emails/update/{email_id}`.

2.  **Controlador (`controllers/emails_controller.py`):**
    - Llama al servicio con el ID y el payload.
    - Responde `404` si el registro no existe.

3.  **Servicio (`services/email_services.py`):**
    - Aplica la actualizacion sobre el email.
    - Retorna el `EmailResponse` actualizado.

### Errores Relevantes

- `404`: Email no encontrado.
- `422`: Fallo de validacion del schema.

## 3. Como Usar

Para actualizar un email, se debe realizar una peticion `PUT` al endpoint `/emails/update/{email_id}` utilizando `application/json`.

### Ejemplo con `curl`:

```bash
curl -X 'PUT' \
  'http://127.0.0.1:8000/emails/update/12' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "status": "sent",
    "error_message": null,
    "sent_at": "2026-02-21T10:30:00"
  }'
```

### Uso desde la Documentacion Interactiva de FastAPI

En `/docs`, el endpoint expone el schema `EmailUpdate` para modificar el estado del registro.

## 4. Impacto

- **Correccion operativa:** Permite ajustar estados o errores de envio registrados.
- **Trazabilidad:** Mantiene consistente el historial del email en base de datos.
