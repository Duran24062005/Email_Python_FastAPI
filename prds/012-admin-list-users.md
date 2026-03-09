# PRD: 012 - Listado General de Usuarios

**Fecha:** 2026-03-09

## 1. Resumen

Esta funcionalidad permite a un administrador consultar la lista paginada de todos los usuarios del sistema.

## 2. Descripcion de la Funcionalidad

### Endpoint

- **Endpoint:** `GET /api/users/admin/all`
- **Tipo de Contenido:** `query params` + `Authorization: Bearer`

### Parametros

El endpoint acepta:

- `page` (int, opcional): Numero de pagina. Por defecto `1`.
- `page_size` (int, opcional): Cantidad de items por pagina. Por defecto `10`, maximo `100`.

### Logica de Implementacion

1.  **Ruta (`routes/user_routes.py`):**
    - Expone `GET /api/users/admin/all`.
    - Requiere rol administrador.

2.  **Middleware (`middlewares/role_middleware.py`):**
    - Verifica que el usuario autenticado tenga `role=admin` y este activo.

3.  **Servicio (`services/user_service.py`):**
    - Obtiene usuarios paginados desde el repositorio.
    - Retorna un `UserList`.

### Errores Relevantes

- `401`: Token invalido, ausente o expirado.
- `403`: Acceso denegado por rol insuficiente o usuario no activo.
- `400`: Paginacion fuera de rango.

## 3. Como Usar

Para listar todos los usuarios, se debe realizar una peticion `GET` al endpoint `/api/users/admin/all` con credenciales de administrador.

### Ejemplo con `curl`:

```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/api/users/admin/all?page=1&page_size=10' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer TU_TOKEN_ADMIN'
```

### Uso desde la Documentacion Interactiva de FastAPI

En `/docs`, el endpoint permite navegar usuarios por pagina una vez autorizado un token de administrador.

## 4. Impacto

- **Visibilidad administrativa:** Centraliza la consulta global de usuarios.
- **Control operativo:** Permite auditar el estado general del sistema.
