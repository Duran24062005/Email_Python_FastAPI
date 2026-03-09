# PRD: 007 - Perfil Propio de Usuario

**Fecha:** 2026-03-09

## 1. Resumen

Esta funcionalidad permite consultar el perfil completo del usuario autenticado desde el modulo de usuarios. Es un endpoint protegido que retorna los datos disponibles en `UserResponse`.

## 2. Descripcion de la Funcionalidad

### Endpoint

- **Endpoint:** `GET /api/users/me`
- **Tipo de Contenido:** `Authorization: Bearer`

### Parametros

El endpoint no recibe body. Requiere:

- `Authorization` (header, requerido): Bearer token valido.

### Logica de Implementacion

1.  **Ruta (`routes/user_routes.py`):**
    - Expone `GET /api/users/me`.
    - Usa `get_current_active_user` y delega al `UserController`.

2.  **Controlador (`controllers/user_controller.py`):**
    - Llama a `get_my_profile`.

3.  **Servicio (`services/user_service.py`):**
    - Busca el usuario por ID.
    - Si existe, lo convierte a `UserResponse`.

### Errores Relevantes

- `401`: Token invalido, ausente o expirado.
- `403`: Usuario inactivo o bloqueado.
- `404`: Usuario no encontrado.

## 3. Como Usar

Para consultar el perfil propio, se debe realizar una peticion `GET` al endpoint `/api/users/me` enviando un Bearer token valido.

### Ejemplo con `curl`:

```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/api/users/me' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer TU_ACCESS_TOKEN'
```

### Uso desde la Documentacion Interactiva de FastAPI

En `/docs`, despues de autorizar el token, este endpoint permite visualizar el perfil actual desde el modulo de usuarios.

## 4. Impacto

- **Autoservicio:** El usuario puede revisar su informacion sin depender de un administrador.
- **Separacion de modulos:** Mantiene el acceso al perfil tambien disponible desde el modulo `users`.
