# PRD: 015 - Consulta de Usuario por ID

**Fecha:** 2026-03-09

## 1. Resumen

Esta funcionalidad permite a un administrador consultar el detalle de un usuario especifico mediante su identificador.

## 2. Descripcion de la Funcionalidad

### Endpoint

- **Endpoint:** `GET /api/users/admin/{user_id}`
- **Tipo de Contenido:** `path param` + `Authorization: Bearer`

### Parametros

El endpoint acepta:

- `user_id` (int, requerido): ID del usuario a consultar.

### Logica de Implementacion

1.  **Ruta (`routes/user_routes.py`):**
    - Expone `GET /api/users/admin/{user_id}`.
    - Requiere rol administrador.

2.  **Servicio (`services/user_service.py`):**
    - Busca el usuario por ID.
    - Si existe, lo retorna como `UserResponse`.

### Errores Relevantes

- `401`: Token invalido, ausente o expirado.
- `403`: Acceso denegado por rol insuficiente o usuario no activo.
- `404`: Usuario no encontrado.

## 3. Como Usar

Para consultar un usuario por ID, se debe realizar una peticion `GET` al endpoint `/api/users/admin/{user_id}` con credenciales de administrador.

### Ejemplo con `curl`:

```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/api/users/admin/7' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer TU_TOKEN_ADMIN'
```

### Uso desde la Documentacion Interactiva de FastAPI

En `/docs`, este endpoint permite capturar el `user_id` y consultar rapidamente el registro del usuario.

## 4. Impacto

- **Soporte administrativo:** Facilita revisar casos puntuales de usuarios.
- **Trazabilidad:** Permite inspeccionar un registro concreto sin recorrer listados.
