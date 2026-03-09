# PRD: 018 - Actualizacion Administrativa de Usuario

**Fecha:** 2026-03-09

## 1. Resumen

Esta funcionalidad permite a un administrador actualizar datos de un usuario existente, incluyendo nombre, email, estado y bandera de verificacion de correo.

## 2. Descripcion de la Funcionalidad

### Endpoint

- **Endpoint:** `PUT /api/users/admin/{user_id}`
- **Tipo de Contenido:** `application/json` + `Authorization: Bearer`

### Parametros

El endpoint acepta:

- `user_id` (int, requerido): ID del usuario a actualizar.
- Body `UserUpdate` con campos opcionales:
  - `name`
  - `email`
  - `status`
  - `email_verify`

### Logica de Implementacion

1.  **Ruta (`routes/user_routes.py`):**
    - Expone `PUT /api/users/admin/{user_id}`.
    - Requiere rol administrador.

2.  **Servicio (`services/user_service.py`):**
    - Busca y actualiza el usuario mediante el repositorio.
    - Solo modifica campos enviados en la solicitud.
    - Retorna el usuario actualizado como `UserResponse`.

### Errores Relevantes

- `401`: Token invalido, ausente o expirado.
- `403`: Acceso denegado por rol insuficiente o usuario no activo.
- `404`: Usuario no encontrado.
- `422`: Fallo de validacion del schema.

## 3. Como Usar

Para actualizar un usuario, se debe realizar una peticion `PUT` al endpoint `/api/users/admin/{user_id}` con un token de administrador.

### Ejemplo con `curl`:

```bash
curl -X 'PUT' \
  'http://127.0.0.1:8000/api/users/admin/7' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer TU_TOKEN_ADMIN' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Nuevo Nombre",
    "email": "nuevo@email.com",
    "status": "active",
    "email_verify": true
  }'
```

### Uso desde la Documentacion Interactiva de FastAPI

En `/docs`, el endpoint muestra todos los campos opcionales de `UserUpdate` para ajustes manuales sobre un usuario existente.

## 4. Impacto

- **Mantenimiento administrativo:** Facilita correcciones manuales de datos.
- **Flexibilidad operativa:** Permite intervenir estado y verificacion sin acciones separadas.
