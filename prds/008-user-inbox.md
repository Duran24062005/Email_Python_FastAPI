# PRD: 008 - Bandeja de Salida del Usuario

**Fecha:** 2026-03-09

## 1. Resumen

Esta funcionalidad permite al usuario autenticado consultar la lista paginada de emails que ha enviado. La respuesta incluye total de registros, pagina actual y tamano de pagina.

## 2. Descripcion de la Funcionalidad

### Endpoint

- **Endpoint:** `GET /api/users/me/inbox`
- **Tipo de Contenido:** `query params` + `Authorization: Bearer`

### Parametros

El endpoint acepta los siguientes query params:

- `page` (int, opcional): Numero de pagina. Valor por defecto `1`.
- `page_size` (int, opcional): Cantidad de items por pagina. Valor por defecto `10`, maximo `100`.

### Logica de Implementacion

1.  **Ruta (`routes/user_routes.py`):**
    - Expone `GET /api/users/me/inbox`.
    - Requiere usuario autenticado y activo.

2.  **Controlador (`controllers/user_controller.py`):**
    - Llama a `get_my_inbox`.

3.  **Servicio (`services/user_service.py`):**
    - Calcula `skip` a partir de `page` y `page_size`.
    - Obtiene los emails del usuario desde el repositorio.
    - Obtiene el total de emails asociados al usuario.
    - Retorna un `EmailList`.

### Errores Relevantes

- `401`: Token invalido, ausente o expirado.
- `403`: Usuario inactivo o bloqueado.
- `422`: Parametros de paginacion invalidos.

## 3. Como Usar

Para consultar la bandeja de salida, se debe realizar una peticion `GET` al endpoint `/api/users/me/inbox` con un Bearer token valido.

### Ejemplo con `curl`:

```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/api/users/me/inbox?page=1&page_size=10' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer TU_ACCESS_TOKEN'
```

### Uso desde la Documentacion Interactiva de FastAPI

En `/docs`, el endpoint permite indicar `page` y `page_size` para navegar el historial de emails del usuario autenticado.

## 4. Impacto

- **Trazabilidad personal:** El usuario puede revisar su historial de envios.
- **Escalabilidad:** La paginacion evita cargar todos los emails en una sola respuesta.
