# PRD: 006 - Perfil Autenticado en Auth

**Fecha:** 2026-03-09

## 1. Resumen

Esta funcionalidad permite obtener el perfil del usuario autenticado desde el modulo de autenticacion. El endpoint requiere un Bearer token valido y devuelve la informacion publica del usuario actual.

## 2. Descripcion de la Funcionalidad

### Endpoint

- **Endpoint:** `GET /api/auth/me`
- **Tipo de Contenido:** `Authorization: Bearer`

### Parametros

El endpoint no recibe body. Requiere:

- `Authorization` (header, requerido): Bearer token valido.

### Logica de Implementacion

1.  **Ruta (`routes/auth_routes.py`):**
    - Expone `GET /api/auth/me`.
    - Usa `get_current_active_user` para validar autenticacion y estado activo.

2.  **Middleware (`middlewares/auth_middleware.py`):**
    - Decodifica el JWT.
    - Busca el usuario en base de datos.
    - Rechaza tokens invalidos, expirados o usuarios no activos.

3.  **Ruta / Respuesta:**
    - Convierte el usuario autenticado a `UserResponse`.
    - No expone la contraseña ni el rol.

### Errores Relevantes

- `401`: Token invalido, ausente o expirado.
- `403`: Usuario inactivo o bloqueado.

## 3. Como Usar

Para obtener el perfil autenticado, se debe realizar una peticion `GET` al endpoint `/api/auth/me` enviando el Bearer token en el header `Authorization`.

### Ejemplo con `curl`:

```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/api/auth/me' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer TU_ACCESS_TOKEN'
```

### Uso desde la Documentacion Interactiva de FastAPI

En `/docs`, primero se debe autorizar el token con el boton `Authorize`. Luego se puede ejecutar `GET /api/auth/me` para consultar el usuario actual.

## 4. Impacto

- **Validacion de sesion:** Permite confirmar que el token sigue siendo valido.
- **Consistencia de seguridad:** Solo responde para usuarios activos.
- **Soporte a clientes:** Facilita cargar datos del usuario actual tras el login.
