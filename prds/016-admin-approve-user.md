# PRD: 016 - Aprobacion de Usuario

**Fecha:** 2026-03-09

## 1. Resumen

Esta funcionalidad permite a un administrador aprobar un usuario cambiando su estado a `active`. Despues del cambio, el sistema intenta enviar un email de notificacion al usuario aprobado.

## 2. Descripcion de la Funcionalidad

### Endpoint

- **Endpoint:** `POST /api/users/admin/{user_id}/approve`
- **Tipo de Contenido:** `path param` + `Authorization: Bearer`

### Parametros

El endpoint acepta:

- `user_id` (int, requerido): ID del usuario a aprobar.

### Logica de Implementacion

1.  **Ruta (`routes/user_routes.py`):**
    - Expone `POST /api/users/admin/{user_id}/approve`.
    - Requiere rol administrador.

2.  **Servicio (`services/user_service.py`):**
    - Busca el usuario por ID.
    - Rechaza la operacion si el usuario ya esta activo.
    - Actualiza el estado a `active`.
    - Intenta enviar un email usando `account_approved.html`.
    - Si el envio falla, la aprobacion no se revierte.

### Errores Relevantes

- `401`: Token invalido, ausente o expirado.
- `403`: Acceso denegado por rol insuficiente o usuario no activo.
- `404`: Usuario no encontrado.
- `409`: El usuario ya esta activo.

## 3. Como Usar

Para aprobar un usuario, se debe realizar una peticion `POST` al endpoint `/api/users/admin/{user_id}/approve` con un token de administrador.

### Ejemplo con `curl`:

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/users/admin/7/approve' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer TU_TOKEN_ADMIN'
```

### Uso desde la Documentacion Interactiva de FastAPI

La documentacion en `/docs` permite indicar el `user_id` y ejecutar la aprobacion desde la interfaz.

## 4. Impacto

- **Habilitacion de acceso:** Convierte al usuario en apto para autenticarse.
- **Notificacion automatica:** Informa al usuario aprobado sin bloquear el cambio de estado.
