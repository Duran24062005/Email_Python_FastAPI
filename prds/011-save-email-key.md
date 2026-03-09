# PRD: 011 - Guardado de Clave SMTP Personal

**Fecha:** 2026-03-09

## 1. Resumen

Esta funcionalidad permite al usuario guardar su propia clave SMTP de aplicacion para utilizar su correo al enviar emails. La clave se almacena en el perfil del usuario.

## 2. Descripcion de la Funcionalidad

### Endpoint

- **Endpoint:** `PUT /api/users/me/email-key`
- **Tipo de Contenido:** `application/json` + `Authorization: Bearer`

### Parametros

El endpoint acepta un cuerpo JSON con el siguiente campo:

- `email_key` (str, requerido): Clave SMTP o contrasena de aplicacion del usuario.

### Logica de Implementacion

1.  **Ruta (`routes/user_routes.py`):**
    - Expone `PUT /api/users/me/email-key`.
    - Requiere usuario autenticado y activo.

2.  **Servicio (`services/user_service.py`):**
    - Recibe la clave y la persiste en el perfil del usuario.
    - Retorna un mensaje simple de confirmacion.

3.  **Repositorio (`repositories/user_repository.py`):**
    - Guarda el valor en `email_key`.

### Errores Relevantes

- `401`: Token invalido, ausente o expirado.
- `403`: Usuario inactivo o bloqueado.
- `422`: Fallo de validacion de entrada.

## 3. Como Usar

Para guardar la clave SMTP personal, se debe realizar una peticion `PUT` al endpoint `/api/users/me/email-key` con un Bearer token valido.

### Ejemplo con `curl`:

```bash
curl -X 'PUT' \
  'http://127.0.0.1:8000/api/users/me/email-key' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer TU_ACCESS_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "email_key": "xxxx xxxx xxxx xxxx"
  }'
```

### Uso desde la Documentacion Interactiva de FastAPI

En `/docs`, el endpoint muestra un campo para guardar la clave SMTP del usuario. La descripcion incluye orientacion para cuentas Gmail.

## 4. Impacto

- **Personalizacion del remitente:** Permite usar la cuenta del usuario al enviar correos.
- **Configuracion individual:** Cada usuario puede mantener su propia clave SMTP en su perfil.
