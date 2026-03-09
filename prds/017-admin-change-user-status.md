# PRD: 017 - Cambio de Estado de Usuario

**Fecha:** 2026-03-09

## 1. Resumen

Esta funcionalidad permite a un administrador cambiar manualmente el estado de un usuario entre `active`, `pending`, `blocked` y `deleted`.

## 2. Descripcion de la Funcionalidad

### Endpoint

- **Endpoint:** `PATCH /api/users/admin/{user_id}/status`
- **Tipo de Contenido:** `application/json` + `Authorization: Bearer`

### Parametros

El endpoint acepta:

- `user_id` (int, requerido): ID del usuario a actualizar.
- `status` (str, requerido): Nuevo estado del usuario.

### Logica de Implementacion

1.  **Ruta (`routes/user_routes.py`):**
    - Expone `PATCH /api/users/admin/{user_id}/status`.
    - Requiere rol administrador.

2.  **Servicio (`services/user_service.py`):**
    - Busca el usuario por ID.
    - Rechaza la operacion si ya tiene el mismo estado.
    - Persiste el nuevo estado.
    - Devuelve un mensaje con el estado aplicado.

### Errores Relevantes

- `401`: Token invalido, ausente o expirado.
- `403`: Acceso denegado por rol insuficiente o usuario no activo.
- `404`: Usuario no encontrado.
- `409`: El usuario ya tiene ese estado.
- `422`: Estado invalido o body incorrecto.

## 3. Como Usar

Para cambiar el estado de un usuario, se debe realizar una peticion `PATCH` al endpoint `/api/users/admin/{user_id}/status`.

### Ejemplo con `curl`:

```bash
curl -X 'PATCH' \
  'http://127.0.0.1:8000/api/users/admin/7/status' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer TU_TOKEN_ADMIN' \
  -H 'Content-Type: application/json' \
  -d '{
    "status": "blocked"
  }'
```

### Uso desde la Documentacion Interactiva de FastAPI

En `/docs`, el endpoint expone el schema `ChangeStatusRequest` con los valores admitidos por el enum.

## 4. Impacto

- **Control administrativo:** Permite habilitar, bloquear o devolver cuentas a estado pendiente.
- **Gobernanza:** Hace explicita la gestion de ciclo de vida del usuario.
