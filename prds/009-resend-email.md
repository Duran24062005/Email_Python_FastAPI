# PRD: 009 - Reenvio de Email

**Fecha:** 2026-03-09

## 1. Resumen

Esta funcionalidad permite reenviar un email previamente enviado por el usuario autenticado. El sistema crea un nuevo registro con el mismo contenido y lo vuelve a enviar al mismo destinatario.

## 2. Descripcion de la Funcionalidad

### Endpoint

- **Endpoint:** `POST /api/users/me/inbox/{email_id}/resend`
- **Tipo de Contenido:** `path param` + `Authorization: Bearer`

### Parametros

El endpoint acepta:

- `email_id` (int, requerido): ID del email que se desea reenviar.

### Logica de Implementacion

1.  **Ruta (`routes/user_routes.py`):**
    - Expone `POST /api/users/me/inbox/{email_id}/resend`.
    - Requiere usuario autenticado y activo.

2.  **Servicio (`services/user_service.py`):**
    - Busca el email original por ID.
    - Verifica que pertenezca al usuario autenticado.
    - Crea un nuevo registro en la base de datos.
    - Intenta reenviar el contenido al mismo destinatario.
    - Actualiza el estado del nuevo registro a `sent` o `failed`.

### Errores Relevantes

- `401`: Token invalido, ausente o expirado.
- `403`: El email no pertenece al usuario autenticado.
- `404`: Email no encontrado.

## 3. Como Usar

Para reenviar un email, se debe realizar una peticion `POST` al endpoint `/api/users/me/inbox/{email_id}/resend` enviando un Bearer token valido.

### Ejemplo con `curl`:

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/users/me/inbox/15/resend' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer TU_ACCESS_TOKEN'
```

### Uso desde la Documentacion Interactiva de FastAPI

En `/docs`, el endpoint permite indicar el `email_id` del registro a reenviar directamente desde la interfaz.

## 4. Impacto

- **Reutilizacion de contenido:** Evita reconstruir manualmente emails ya enviados.
- **Auditoria:** Cada reenvio crea un nuevo registro independiente en la base de datos.
