# PRD: 014 - Estadisticas de Usuarios

**Fecha:** 2026-03-09

## 1. Resumen

Esta funcionalidad permite consultar estadisticas generales de usuarios para uso administrativo, incluyendo total de usuarios, usuarios pendientes y usuarios activos calculados.

## 2. Descripcion de la Funcionalidad

### Endpoint

- **Endpoint:** `GET /api/users/admin/stats`
- **Tipo de Contenido:** `Authorization: Bearer`

### Parametros

El endpoint no recibe body ni query params. Requiere:

- `Authorization` (header, requerido): Bearer token de administrador.

### Logica de Implementacion

1.  **Ruta (`routes/user_routes.py`):**
    - Expone `GET /api/users/admin/stats`.
    - Requiere rol administrador.

2.  **Servicio (`services/user_service.py`):**
    - Obtiene el total de usuarios.
    - Obtiene la lista de usuarios pendientes.
    - Calcula `active_users` como `total_users - pending_users`.

### Respuesta Esperada

La respuesta incluye:

- `total_users`
- `pending_users`
- `active_users`

### Errores Relevantes

- `401`: Token invalido, ausente o expirado.
- `403`: Acceso denegado por rol insuficiente o usuario no activo.

## 3. Como Usar

Para consultar las estadisticas, se debe realizar una peticion `GET` al endpoint `/api/users/admin/stats` con un token de administrador.

### Ejemplo con `curl`:

```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/api/users/admin/stats' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer TU_TOKEN_ADMIN'
```

### Uso desde la Documentacion Interactiva de FastAPI

En `/docs`, el endpoint permite ejecutar la consulta de metricas administrativas sin parametros adicionales.

## 4. Impacto

- **Monitoreo administrativo:** Ofrece un resumen rapido del estado de usuarios.
- **Soporte a reporting:** Facilita tableros simples y seguimiento operativo.
