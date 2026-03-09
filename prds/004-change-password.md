# PRD: 004 - Cambio de Contrasena

**Fecha:** 2026-03-09

## 1. Resumen

Esta funcionalidad permite que un usuario autenticado cambie su propia contraseña. El endpoint exige un Bearer token válido, valida la contraseña actual antes de aceptar el cambio y persiste un nuevo hash bcrypt para reemplazar la credencial anterior.

## 2. Descripción de la Funcionalidad

### Endpoint

- **Endpoint:** `POST /api/auth/change-password`
- **Tipo de Contenido:** `application/json`
- **Autenticación:** Bearer token requerido

### Parámetros

El endpoint acepta un cuerpo JSON con los siguientes campos:

- `current_password` (str, requerido): Contraseña actual del usuario. No debe exceder 72 bytes.
- `new_password` (str, requerido): Nueva contraseña. Debe tener al menos 8 caracteres y no exceder 72 bytes.

### Lógica de Implementación

1.  **Ruta (`routes/auth_routes.py`):**
    - Expone el endpoint `POST /api/auth/change-password`.
    - Requiere un usuario autenticado mediante `get_current_active_user`.
    - Recibe el schema `ChangePasswordRequest` y delega la operación al `AuthController`.

2.  **Middleware / Dependencia de autenticación:**
    - Valida el Bearer token.
    - Restringe el acceso a usuarios activos.

3.  **Controlador (`controllers/auth_controller.py`):**
    - Llama a `AuthService.change_password`.
    - Devuelve el mensaje de confirmación o el error HTTP correspondiente.

4.  **Servicio (`services/auth_service.py`):**
    - Obtiene al usuario autenticado desde el repositorio.
    - Verifica que `current_password` coincida con el hash almacenado.
    - Genera un nuevo hash bcrypt con `new_password`.
    - Actualiza la contraseña almacenada.

5.  **Repositorio (`repositories/user_repository.py`):**
    - Persiste el nuevo hash de la contraseña.
    - Actualiza la fecha `updated_at` del usuario.

### Respuesta Esperada

La respuesta devuelve un mensaje simple de confirmación:

- `message`: `"Contraseña actualizada correctamente"`

### Errores Relevantes

- `400`: La contraseña actual es incorrecta.
- `401`: Token inválido o ausente en una ruta protegida.
- `403`: Usuario no activo.
- `422`: Falló la validación de entrada, incluyendo nueva contraseña menor a 8 caracteres o cualquier contraseña mayor a 72 bytes.

## 3. Cómo Usar

Para cambiar la contraseña, se debe realizar una petición `POST` al endpoint `/api/auth/change-password` utilizando `application/json` y enviando un Bearer token válido en el header `Authorization`.

### Ejemplo con `curl`:

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/auth/change-password' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer TU_ACCESS_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "current_password": "passwordActual",
    "new_password": "nuevaPassword123"
  }'
```

### Uso desde la Documentación Interactiva de FastAPI

En `/docs`, primero se debe autorizar el Bearer token con el botón `Authorize`. Después de eso, el endpoint permite enviar la contraseña actual y la nueva contraseña desde la interfaz.

## 4. Impacto

- **Autogestión de credenciales:** El usuario puede actualizar su contraseña sin intervención administrativa.
- **Seguridad:** El cambio exige confirmar la contraseña actual antes de reemplazarla.
- **Protección de datos sensibles:** La nueva contraseña se almacena únicamente como hash bcrypt.
- **Dependencia de autenticación:** Solo usuarios autenticados y activos pueden ejecutar esta operación.
