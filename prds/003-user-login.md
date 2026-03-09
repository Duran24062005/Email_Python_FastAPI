# PRD: 003 - Inicio de Sesion de Usuario

**Fecha:** 2026-03-09

## 1. Resumen

Esta funcionalidad permite autenticar a un usuario mediante email y contraseña para obtener un token JWT de acceso. El sistema valida las credenciales, confirma que la cuenta esté activa y actualiza la fecha del último inicio de sesión antes de retornar el token Bearer y el perfil del usuario autenticado.

## 2. Descripción de la Funcionalidad

### Endpoint

- **Endpoint:** `POST /api/auth/login`
- **Tipo de Contenido:** `application/json`

### Parámetros

El endpoint acepta un cuerpo JSON con los siguientes campos:

- `email` (str, requerido): Correo electrónico del usuario.
- `password` (str, requerido): Contraseña del usuario. No debe exceder 72 bytes.

### Lógica de Implementación

1.  **Ruta (`routes/auth_routes.py`):**
    - Expone el endpoint `POST /api/auth/login`.
    - Recibe el schema `LoginRequest` y delega la operación al `AuthController`.

2.  **Controlador (`controllers/auth_controller.py`):**
    - Orquesta la autenticación mediante `AuthService`.
    - Retorna el `TokenResponse` o el error HTTP correspondiente.

3.  **Servicio (`services/auth_service.py`):**
    - Busca el usuario por email.
    - Verifica la contraseña enviada contra el hash almacenado.
    - Rechaza el acceso si el usuario está bloqueado.
    - Rechaza el acceso si el usuario no está en estado `active`.
    - Actualiza `last_login` al momento de autenticación exitosa.
    - Genera un token JWT de acceso.

4.  **Repositorio (`repositories/user_repository.py`):**
    - Consulta al usuario por email.
    - Actualiza el campo `last_login` después del login exitoso.

### Respuesta Esperada

La respuesta incluye la información de autenticación y el perfil del usuario:

- `access_token` (str): JWT de acceso.
- `token_type` (str): Siempre retorna `bearer`.
- `expires_in` (int): Tiempo de vigencia del token en segundos. Actualmente `1800`.
- `user` (obj): Perfil del usuario autenticado.

### Errores Relevantes

- `401`: Credenciales incorrectas.
- `403`: Usuario bloqueado.
- `403`: Cuenta no activa.
- `422`: Falló la validación de entrada, incluyendo contraseña mayor a 72 bytes.

## 3. Cómo Usar

Para iniciar sesión, se debe realizar una petición `POST` al endpoint `/api/auth/login` utilizando `application/json`.

### Ejemplo con `curl`:

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/auth/login' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "juan@example.com",
    "password": "securepassword123"
  }'
```

### Uso desde la Documentación Interactiva de FastAPI

La documentación en `/docs` permite ejecutar el login y copiar el token de respuesta para usarlo como Bearer token en los endpoints protegidos.

## 4. Impacto

- **Acceso autenticado:** Es la puerta de entrada a todas las rutas protegidas del sistema.
- **Control de estado:** Impide autenticación de usuarios bloqueados o no activos.
- **Trazabilidad:** Actualiza `last_login`, permitiendo registrar el último acceso exitoso.
- **Seguridad de sesión:** Emite un JWT con vigencia limitada para consumir endpoints protegidos.
