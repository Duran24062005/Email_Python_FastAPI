# PRD: 013 - Listado de Usuarios Pendientes

**Fecha:** 2026-03-09

## 1. Resumen

Esta funcionalidad permite a un administrador consultar los usuarios con estado `pending` que aun esperan aprobacion.

## 2. Descripcion de la Funcionalidad

### Endpoint

- **Endpoint:** `GET /api/users/admin/pending`
- **Tipo de Contenido:** `query params` + `Authorization: Bearer`

### Parametros

El endpoint acepta:

- `page` (int, opcional): Numero de pagina. Por defecto `1`.
- `page_size` (int, opcional): Cantidad de items por pagina. Por defecto `10`, maximo `100`.

### Logica de Implementacion

1.  **Ruta (`routes/user_routes.py`):**
    - Expone `GET /api/users/admin/pending`.
    - Requiere rol administrador.

2.  **Servicio (`services/user_service.py`):**
    - Consulta todos los usuarios con estado `pending`.
    - Aplica paginacion manual sobre esa lista.
    - Retorna un `UserList`.

### Errores Relevantes

- `401`: Token invalido, ausente o expirado.
- `403`: Acceso denegado por rol insuficiente o usuario no activo.
- `422`: Query params invalidos.

## 3. Como Usar

Para listar usuarios pendientes, se debe realizar una peticion `GET` al endpoint `/api/users/admin/pending` con un token de administrador.

### Ejemplo con `curl`:

```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/api/users/admin/pending?page=1&page_size=10' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer TU_TOKEN_ADMIN'
```

### Uso desde la Documentacion Interactiva de FastAPI

La documentacion en `/docs` permite filtrar y revisar usuarios pendientes desde el panel de administracion de la API.

## 4. Impacto

- **Priorizacion operativa:** Facilita revisar cuentas que esperan accion administrativa.
- **Soporte al flujo de aprobacion:** Funciona como entrada para aprobar usuarios.
