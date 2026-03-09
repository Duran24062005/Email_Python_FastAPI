# PRD: 005 - Verificacion de Email

**Fecha:** 2026-03-09

## 1. Resumen

Esta funcionalidad permite confirmar la direccion de correo de un usuario mediante un token enviado automaticamente despues del registro. Cuando el token es valido, el sistema marca el campo `email_verify` como `true`.

## 2. Descripcion de la Funcionalidad

### Endpoint

- **Endpoint:** `GET /api/users/verify-email`
- **Tipo de Contenido:** `query params`

### Parametros

El endpoint recibe el siguiente parametro en la URL:

- `token` (str, requerido): Token de verificacion recibido por correo.

### Logica de Implementacion

1.  **Ruta (`routes/user_routes.py`):**
    - Expone el endpoint `GET /api/users/verify-email`.
    - Recibe el token por query string y delega la validacion al `UserController`.

2.  **Controlador (`controllers/user_controller.py`):**
    - Llama al metodo `verify_email` del servicio.

3.  **Servicio (`services/user_service.py`):**
    - Decodifica el token JWT.
    - Valida que el `purpose` sea `email_verification`.
    - Verifica que el usuario exista.
    - Si el email ya estaba verificado, retorna un mensaje informativo.
    - Si todo es correcto, actualiza `email_verify=true`.

4.  **Repositorio (`repositories/user_repository.py`):**
    - Marca el email como verificado y actualiza `updated_at`.

### Errores Relevantes

- `400`: Token expirado.
- `400`: Token invalido o con `purpose` incorrecto.
- `404`: Usuario no encontrado.

## 3. Como Usar

Para verificar un email, se debe abrir el enlace enviado por correo o realizar una peticion `GET` al endpoint `/api/users/verify-email` con el token en la URL.

### Ejemplo con `curl`:

```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/api/users/verify-email?token=TU_TOKEN_DE_VERIFICACION' \
  -H 'accept: application/json'
```

### Uso desde la Documentacion Interactiva de FastAPI

La documentacion en `/docs` permite pegar manualmente el token en el parametro `token` y ejecutar la verificacion desde la interfaz.

## 4. Impacto

- **Confirmacion de identidad:** Permite marcar si el correo del usuario fue validado.
- **Integracion con registro:** Depende del token generado durante el alta de usuario.
- **Experiencia de usuario:** Si el email ya estaba verificado, evita fallar y devuelve un mensaje reutilizable.
