# PRD: 019 - Eliminacion de Usuario

**Fecha:** 2026-03-09

## 1. Resumen

Esta funcionalidad permite a un administrador eliminar un usuario del sistema mediante su ID.

## 2. Descripcion de la Funcionalidad

### Endpoint

- **Endpoint:** `DELETE /api/users/admin/{user_id}`
- **Tipo de Contenido:** `path param` + `Authorization: Bearer`

### Parametros

El endpoint acepta:

- `user_id` (int, requerido): ID del usuario a eliminar.

### Logica de Implementacion

1.  **Ruta (`routes/user_routes.py`):**
    - Expone `DELETE /api/users/admin/{user_id}`.
    - Requiere rol administrador.

2.  **Servicio (`services/user_service.py`):**
    - Solicita al repositorio eliminar el usuario.
    - Si no existe, devuelve error `404`.
    - Si la eliminacion se completa, retorna un mensaje de confirmacion.

3.  **Repositorio (`repositories/user_repository.py`):**
    - Ejecuta eliminacion fisica del registro en base de datos.

### Errores Relevantes

- `401`: Token invalido, ausente o expirado.
- `403`: Acceso denegado por rol insuficiente o usuario no activo.
- `404`: Usuario no encontrado.

## 3. Como Usar

Para eliminar un usuario, se debe realizar una peticion `DELETE` al endpoint `/api/users/admin/{user_id}` con credenciales de administrador.

### Ejemplo con `curl`:

```bash
curl -X 'DELETE' \
  'http://127.0.0.1:8000/api/users/admin/7' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer TU_TOKEN_ADMIN'
```

### Uso desde la Documentacion Interactiva de FastAPI

En `/docs`, el endpoint permite indicar el `user_id` y ejecutar la eliminacion desde la interfaz.

## 4. Impacto

- **Control de datos:** Permite retirar cuentas del sistema.
- **Operacion sensible:** Debe ser usada solo por administradores autenticados.
