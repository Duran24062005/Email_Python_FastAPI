# PRD: 002 - Registro de Usuario

**Fecha:** 2026-03-09

## 1. Resumen

Esta funcionalidad permite registrar nuevos usuarios en el sistema mediante el endpoint de autenticación. Durante el proceso se valida que el email no exista previamente, se hashea la contraseña con bcrypt y se crea la cuenta con estado activo. Después del registro, el sistema intenta enviar automáticamente un correo de verificación, sin bloquear la creación del usuario si el envío falla.

## 2. Descripción de la Funcionalidad

### Endpoint

- **Endpoint:** `POST /api/auth/register`
- **Tipo de Contenido:** `application/json`

### Parámetros

El endpoint acepta un cuerpo JSON con los siguientes campos:

- `name` (str, requerido): Nombre del usuario.
- `email` (str, requerido): Correo electrónico del usuario. Debe ser único.
- `password` (str, requerido): Contraseña del usuario. Debe tener al menos 8 caracteres y no exceder 72 bytes.

### Lógica de Implementación

1.  **Ruta (`routes/auth_routes.py`):**
    - Expone el endpoint `POST /api/auth/register`.
    - Recibe el schema `UserCreate` y delega la operación al `AuthController`.

2.  **Controlador (`controllers/auth_controller.py`):**
    - Orquesta la llamada al `AuthService`.
    - Mapea las excepciones de dominio a respuestas HTTP.

3.  **Servicio (`services/auth_service.py`):**
    - Verifica si ya existe un usuario con el mismo email.
    - Hashea la contraseña usando bcrypt.
    - Crea el usuario llamando al repositorio.
    - Intenta enviar un correo de verificación con un token JWT válido por 24 horas.
    - Si el envío del correo falla, el registro igualmente se completa.

4.  **Repositorio (`repositories/user_repository.py`):**
    - Guarda el usuario con `role=general`, `status=active` y `email_verify=false`.
    - Persiste el hash de la contraseña en lugar del valor plano.

### Respuesta Esperada

La respuesta devuelve el perfil del usuario recién creado, sin exponer la contraseña:

- `id`
- `name`
- `email`
- `status`
- `email_verify`
- `last_login`
- `created_at`
- `updated_at`

### Errores Relevantes

- `409`: El email ya está registrado.
- `422`: Falló la validación de entrada, incluyendo contraseña menor a 8 caracteres o mayor a 72 bytes.

## 3. Cómo Usar

Para registrar un usuario, se debe realizar una petición `POST` al endpoint `/api/auth/register` utilizando `application/json`.

### Ejemplo con `curl`:

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/auth/register' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Juan Perez",
    "email": "juan@example.com",
    "password": "securepassword123"
  }'
```

### Uso desde la Documentación Interactiva de FastAPI

La documentación en `/docs` muestra este endpoint con el schema `UserCreate`, permitiendo capturar el nombre, email y contraseña desde la interfaz web.

## 4. Impacto

- **Alta de usuarios:** Habilita el acceso inicial al sistema para nuevos usuarios.
- **Seguridad:** La contraseña nunca se almacena en texto plano; siempre se persiste como hash bcrypt.
- **Verificación por correo:** El sistema envía un enlace de verificación tras el registro, pero este flujo no bloquea la creación de la cuenta.
- **Dependencia para autenticación:** El usuario creado queda disponible para iniciar sesión de inmediato, ya que se registra con `status=active`.
