# PRD: 024 - Eliminacion de Email

**Fecha:** 2026-03-09

## 1. Resumen

Esta funcionalidad permite eliminar un registro de email existente del modulo `emails`.

## 2. Descripcion de la Funcionalidad

### Endpoint

- **Endpoint:** `DELETE /emails/{email_id}`
- **Tipo de Contenido:** `path param`

### Parametros

El endpoint acepta:

- `email_id` (int, requerido): ID del email a eliminar.

### Logica de Implementacion

1.  **Ruta (`routes/email_routes.py`):**
    - Expone `DELETE /emails/{email_id}`.

2.  **Controlador (`controllers/emails_controller.py`):**
    - Solicita al servicio la eliminacion del registro.
    - Si el email no existe, responde `404`.

3.  **Servicio (`services/email_services.py`):**
    - Elimina el email desde el repositorio y retorna el resultado.

### Errores Relevantes

- `404`: Email no encontrado.

## 3. Como Usar

Para eliminar un email, se debe realizar una peticion `DELETE` al endpoint `/emails/{email_id}`.

### Ejemplo con `curl`:

```bash
curl -X 'DELETE' \
  'http://127.0.0.1:8000/emails/12' \
  -H 'accept: application/json'
```

### Uso desde la Documentacion Interactiva de FastAPI

En `/docs`, el endpoint permite indicar el `email_id` y ejecutar la eliminacion del registro.

## 4. Impacto

- **Mantenimiento de datos:** Permite retirar registros de email del sistema.
- **Operacion irreversible a nivel de registro:** El endpoint elimina el email de la base de datos.
