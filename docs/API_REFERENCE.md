# 📖 API Reference — Email Python FastAPI

> Referencia completa de todos los endpoints. La documentación interactiva (Swagger UI) está disponible en `http://localhost:8001/` cuando la aplicación está corriendo.

---

## Autenticación

Las rutas protegidas requieren un **Bearer token** en el header:

```
Authorization: Bearer <access_token>
```

El token se obtiene en `POST /api/auth/login`. Su vigencia es `ACCESS_TOKEN_EXPIRE_MINUTES` minutos (el `TokenResponse` incluye `expires_in: 1800` como referencia).

---

## Módulo Auth — `/api/auth`

### `POST /api/auth/register` · 201

Registra un nuevo usuario. Hashea la contraseña con bcrypt y envía un email de verificación automáticamente.

**Body (`UserCreate`):**
```json
{
  "name": "Juan Pérez",
  "email": "juan@example.com",
  "password": "securepassword123"
}
```

Restricciones: `password` mínimo 8 caracteres, máximo 72 bytes (límite de bcrypt).

**Respuesta 201 (`UserResponse`):**
```json
{
  "id": 1,
  "name": "Juan Pérez",
  "email": "juan@example.com",
  "status": "active",
  "email_verify": false,
  "last_login": null,
  "created_at": "2026-02-21T10:00:00",
  "updated_at": "2026-02-21T10:00:00"
}
```

**Efectos secundarios:** envía email de verificación con token JWT válido por 24 horas. Si el envío falla, el registro se completa igualmente.

| Código | Motivo |
|---|---|
| `409` | Email ya registrado |
| `422` | Contraseña excede 72 bytes o falla validación Pydantic |

---

### `POST /api/auth/login` · 200

Autentica al usuario y retorna un JWT de acceso.

**Body (`LoginRequest`):**
```json
{
  "email": "juan@example.com",
  "password": "securepassword123"
}
```

**Respuesta 200 (`TokenResponse`):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": { ...UserResponse }
}
```

| Código | Motivo |
|---|---|
| `401` | Credenciales incorrectas (email no existe o contraseña errónea) |
| `403` | Usuario bloqueado (`status: blocked`) |
| `403` | Cuenta pendiente de activación (`status: pending`) |

---

### `GET /api/auth/me` · 200

🔒 Requiere Bearer token activo.

Retorna el perfil del usuario autenticado.

**Respuesta 200:** `UserResponse`

---

### `POST /api/auth/change-password` · 200

🔒 Requiere Bearer token activo.

Cambia la contraseña del usuario autenticado.

**Body (`ChangePasswordRequest`):**
```json
{
  "current_password": "passwordActual",
  "new_password": "nuevaPassword123"
}
```

**Respuesta 200:**
```json
{ "message": "Contraseña actualizada correctamente" }
```

| Código | Motivo |
|---|---|
| `400` | Contraseña actual incorrecta |

---

## Módulo Users — `/api/users`

### Rutas Públicas

### `GET /api/users/verify-email?token=<JWT>` · 200

Verifica el email del usuario con el token recibido por correo al registrarse.

**Query param:** `token` (string, requerido)

**Respuesta 200:**
```json
{ "message": "Email verificado exitosamente" }
```

Si ya estaba verificado:
```json
{ "message": "El email ya estaba verificado" }
```

| Código | Motivo |
|---|---|
| `400` | Token expirado (`ExpiredSignatureError`) |
| `400` | Token inválido o `purpose != "email_verification"` |
| `404` | Usuario no encontrado |

---

### Rutas de Usuario General

🔒 Todas requieren Bearer token con `status == active`.

### `GET /api/users/me` · 200

Retorna el perfil completo del usuario autenticado.

**Respuesta 200:** `UserResponse`

---

### `GET /api/users/me/inbox` · 200

Bandeja de salida del usuario: todos sus emails enviados, paginados y ordenados por `created_at DESC`.

**Query params:**
- `page` (int, default: `1`, mínimo: `1`)
- `page_size` (int, default: `10`, rango: `1-100`)

**Respuesta 200 (`EmailList`):**
```json
{
  "emails": [ ...EmailResponse ],
  "total": 42,
  "page": 1,
  "page_size": 10
}
```

---

### `POST /api/users/me/inbox/{email_id}/resend` · 201

Reenvía un email existente. Crea un nuevo registro en la BD con el mismo contenido y lo envía al mismo destinatario.

**Path param:** `email_id` (int)

**Respuesta 201:** `EmailResponse`

| Código | Motivo |
|---|---|
| `403` | El email no pertenece al usuario autenticado |
| `404` | Email no encontrado |

---

### `POST /api/users/me/send-template` · 201

Envía un email usando una plantilla HTML del sistema.

**Body (`SendWithTemplateRequest`):**
```json
{
  "recipient": "cliente@example.com",
  "subject": "Bienvenido a nuestra plataforma",
  "template_name": "welcome.html",
  "template_data": {
    "nombre": "Juan Pérez",
    "empresa": "Mi Empresa",
    "mensaje_adicional": "Gracias por registrarte"
  }
}
```

**Plantillas disponibles:**

| `template_name` | Variables requeridas | Variables opcionales |
|---|---|---|
| `welcome.html` | `nombre`, `empresa` | `mensaje_adicional`, `link_accion` |
| `welcome_educonnect.html` | `nombre`, `empresa` | `mensaje_adicional`, `link_accion` |
| `account_approved.html` | `nombre`, `empresa`, `role`, `login_link` | — |
| `my_website.html` | `nombre` | — |

**Respuesta 201:** `EmailResponse`

| Código | Motivo |
|---|---|
| `404` | Plantilla no encontrada en `templates/` |

---

### `PUT /api/users/me/email-key` · 200

Guarda la contraseña de aplicación SMTP personal del usuario en su perfil.

**Body (`SaveEmailKeyRequest`):**
```json
{
  "email_key": "xxxx xxxx xxxx xxxx"
}
```

**Respuesta 200:**
```json
{ "message": "Email key guardada correctamente" }
```

> Para Gmail: Cuenta → Seguridad → Verificación en 2 pasos → Contraseñas de aplicaciones.

---

### Rutas de Administrador

🔒 Requieren Bearer token con `role == admin` y `status == active`. Retornan `403` si no se cumplen ambas condiciones.

### `GET /api/users/admin/all` · 200

Lista todos los usuarios del sistema paginados.

**Query params:** `page`, `page_size`

**Respuesta 200:** `UserList`

---

### `GET /api/users/admin/pending` · 200

Lista usuarios con `status == pending` que esperan aprobación.

**Query params:** `page`, `page_size`

**Respuesta 200:** `UserList`

---

### `GET /api/users/admin/stats` · 200

Estadísticas generales de usuarios.

**Respuesta 200:**
```json
{
  "total_users": 42,
  "pending_users": 5,
  "active_users": 37
}
```

> `active_users` se calcula como `total_users - pending_users` (no filtra por status directamente).

---

### `GET /api/users/admin/{user_id}` · 200

Obtiene un usuario específico por ID.

**Respuesta 200:** `UserResponse`

| Código | Motivo |
|---|---|
| `404` | Usuario no encontrado |

---

### `POST /api/users/admin/{user_id}/approve` · 200

Aprueba un usuario cambiando su `status` a `active`. Envía automáticamente un email de notificación usando `account_approved.html`.

**Respuesta 200:**
```json
{ "message": "Usuario Juan aprobado correctamente" }
```

| Código | Motivo |
|---|---|
| `404` | Usuario no encontrado |
| `409` | El usuario ya está activo |

---

### `PATCH /api/users/admin/{user_id}/status` · 200

Cambia el estado de un usuario.

**Body (`ChangeStatusRequest`):**
```json
{ "status": "blocked" }
```

**Valores válidos de `status`:** `active`, `pending`, `blocked`, `deleted`

**Respuesta 200:**
```json
{
  "message": "Estado del usuario actualizado a 'blocked'",
  "user_id": 5
}
```

| Código | Motivo |
|---|---|
| `404` | Usuario no encontrado |
| `409` | El usuario ya tiene ese estado |

---

### `PUT /api/users/admin/{user_id}` · 200

Actualiza los datos de un usuario. Todos los campos son opcionales.

**Body (`UserUpdate`):**
```json
{
  "name": "Nuevo Nombre",
  "email": "nuevo@email.com",
  "status": "active",
  "email_verify": true
}
```

**Respuesta 200:** `UserResponse`

---

### `DELETE /api/users/admin/{user_id}` · 200

Elimina un usuario del sistema (eliminación física en BD).

**Respuesta 200:**
```json
{ "message": "Usuario 5 eliminado correctamente" }
```

---

## Módulo Emails — `/emails`

Pipeline interno de gestión de emails.

### `GET /emails/` · 200

Lista paginada de todos los emails del sistema.

**Query params:** `page` (default: `1`), `page_size` (default: `10`, máx: `100`)

**Respuesta 200:** `EmailList`

---

### `GET /emails/{email_id}` · 200

Obtiene un email por ID.

**Respuesta 200:** `EmailResponse`

| Código | Motivo |
|---|---|
| `404` | Email no encontrado |

---

### `POST /emails/send` · 201

Envía un email. Soporta texto plano, HTML directo o plantilla Jinja2.

**Body (`EmailCreate`):**
```json
{
  "user_id": 1,
  "recipient": "usuario@example.com",
  "subject": "Asunto",
  "body": "Texto plano",
  "html_body": "<h1>HTML opcional</h1>",
  "template_name": "welcome.html",
  "template_data": { "nombre": "Juan", "empresa": "Corp" }
}
```

Prioridad de contenido: `html_body` directo → plantilla → `body` como HTML básico.

**Respuesta 201:** `EmailResponse`

| Código | Motivo |
|---|---|
| `500` | Email enviado pero con `status: failed` |

---

### `PUT /emails/update/{email_id}` · 200

Actualiza el estado de un email existente.

**Body (`EmailUpdate`):**
```json
{
  "status": "sent",
  "error_message": null,
  "sent_at": "2026-02-21T10:30:00"
}
```

**Respuesta 200:** `EmailResponse`

| Código | Motivo |
|---|---|
| `404` | Email no encontrado |

---

### `DELETE /emails/{email_id}` · 200

Elimina un email del registro.

**Respuesta 200:**
```json
{ "message": "Email 3 deleted successfully" }
```

---

## Schemas de Respuesta

### `UserResponse`
```json
{
  "id": 1,
  "name": "Juan Pérez",
  "email": "juan@example.com",
  "status": "active",
  "email_verify": true,
  "last_login": "2026-02-21T09:00:00",
  "created_at": "2026-01-01T00:00:00",
  "updated_at": "2026-02-21T09:00:00"
}
```

> El campo `role` no se incluye en `UserResponse` (omitido del schema Pydantic por seguridad).

### `UserList`
```json
{
  "users": [ ...UserResponse ],
  "total": 42,
  "page": 1,
  "page_size": 10
}
```

### `EmailResponse`
```json
{
  "id": 7,
  "user_id": 1,
  "recipient": "cliente@example.com",
  "subject": "Bienvenido",
  "body": "Texto plano...",
  "html_body": "<html>...</html>",
  "status": "sent",
  "sent_at": "2026-02-21T10:30:00",
  "error_message": null,
  "created_at": "2026-02-21T10:29:55",
  "updated_at": "2026-02-21T10:30:00"
}
```

### `EmailList`
```json
{
  "emails": [ ...EmailResponse ],
  "total": 42,
  "page": 1,
  "page_size": 10
}
```

### `TokenResponse`
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": { ...UserResponse }
}
```

---

## Tabla de Códigos de Error

| Código | Significado | Ejemplos |
|---|---|---|
| `400` | Solicitud inválida | Token expirado, contraseña actual incorrecta |
| `401` | No autenticado | JWT faltante, firma inválida, expirado |
| `403` | Sin permisos | Usuario bloqueado, rol insuficiente, email ajeno |
| `404` | Recurso no encontrado | Usuario, email o plantilla inexistente |
| `409` | Conflicto de estado | Email duplicado, usuario ya activo, estado igual |
| `422` | Error de validación | Pydantic falla (campo requerido, tipo incorrecto) |
| `500` | Error interno | Error inesperado del servidor |

---

## Resumen de Endpoints

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| POST | `/api/auth/register` | — | Registrar usuario |
| POST | `/api/auth/login` | — | Login → JWT |
| GET | `/api/auth/me` | User | Perfil propio |
| POST | `/api/auth/change-password` | User | Cambiar contraseña |
| GET | `/api/users/verify-email` | — | Verificar email |
| GET | `/api/users/me` | User | Perfil propio |
| GET | `/api/users/me/inbox` | User | Bandeja de salida |
| POST | `/api/users/me/inbox/{id}/resend` | User | Reenviar email |
| POST | `/api/users/me/send-template` | User | Enviar con plantilla |
| PUT | `/api/users/me/email-key` | User | Guardar clave SMTP |
| GET | `/api/users/admin/all` | Admin | Todos los usuarios |
| GET | `/api/users/admin/pending` | Admin | Usuarios pendientes |
| GET | `/api/users/admin/stats` | Admin | Estadísticas |
| GET | `/api/users/admin/{id}` | Admin | Usuario por ID |
| POST | `/api/users/admin/{id}/approve` | Admin | Aprobar usuario |
| PATCH | `/api/users/admin/{id}/status` | Admin | Cambiar estado |
| PUT | `/api/users/admin/{id}` | Admin | Actualizar usuario |
| DELETE | `/api/users/admin/{id}` | Admin | Eliminar usuario |
| GET | `/emails/` | — | Listar emails |
| GET | `/emails/{id}` | — | Email por ID |
| POST | `/emails/send` | — | Enviar email |
| PUT | `/emails/update/{id}` | — | Actualizar email |
| DELETE | `/emails/{id}` | — | Eliminar email |