# PRD: 021 - Consulta de Email por ID

**Fecha:** 2026-03-09

## 1. Resumen

Esta funcionalidad permite obtener el detalle de un email especifico mediante su identificador.

## 2. Descripcion de la Funcionalidad

### Endpoint

- **Endpoint:** `GET /emails/{email_id}`
- **Tipo de Contenido:** `path param`

### Parametros

El endpoint acepta:

- `email_id` (int, requerido): ID del email a consultar.

### Logica de Implementacion

1.  **Ruta (`routes/email_routes.py`):**
    - Expone `GET /emails/{email_id}`.

2.  **Controlador (`controllers/emails_controller.py`):**
    - Busca el email por ID.
    - Si no existe, responde `404`.

3.  **Servicio (`services/email_services.py`):**
    - Consulta el registro en el repositorio.
    - Retorna el objeto `EmailResponse` si existe.

### Errores Relevantes

- `404`: Email no encontrado.

## 3. Como Usar

Para obtener el detalle de un email, se debe realizar una peticion `GET` al endpoint `/emails/{email_id}`.

### Ejemplo con `curl`:

```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/emails/12' \
  -H 'accept: application/json'
```

### Uso desde la Documentacion Interactiva de FastAPI

En `/docs`, el endpoint permite capturar el `email_id` y revisar el detalle completo del registro.

## 4. Impacto

- **Diagnostico:** Permite inspeccionar un email concreto, su estado y posibles errores.
- **Soporte operativo:** Facilita investigar casos puntuales de envio.
