# Documentación de la API - Email Service

Esta es la documentación de referencia para todos los endpoints disponibles en la API de envío de correos.

## Autenticación

La mayoría de los endpoints requieren autenticación mediante un **Bearer Token** en el header `Authorization`.

`Authorization: Bearer <TU_TOKEN_JWT>`

## Endpoints de Autenticación (`/auth`)

---

### 1. Registrar un Nuevo Usuario

- **Endpoint:** `POST /auth/register`
- **Descripción:** Registra un nuevo usuario en el sistema. El email debe ser único. Tras el registro, el usuario recibe un correo para verificar su cuenta.
- **Request Body:**
  ```json
  {
    "name": "Nombre Apellido",
    "email": "usuario@example.com",
    "password": "tu-contraseña-segura",
    "role": "user"
  }
  ```
- **Respuesta Exitosa (201):**
  - Devuelve el perfil del usuario recién creado (sin la contraseña).

---

### 2. Iniciar Sesión

- **Endpoint:** `POST /auth/login`
- **Descripción:** Autentica a un usuario con su email and contraseña. La cuenta debe estar en estado `ACTIVE`.
- **Request Body:**
  ```json
  {
    "username": "usuario@example.com",
    "password": "tu-contraseña"
  }
  ```
- **Respuesta Exitosa (200):**
  - Devuelve un `access_token` JWT válido por 30 minutos.
  ```json
  {
    "access_token": "ey...",
    "token_type": "bearer"
  }
  ```

---

### 3. Obtener Perfil del Usuario Autenticado

- **Endpoint:** `GET /auth/me`
- **Descripción:** Devuelve el perfil del usuario que realiza la petición.
- **Autenticación:** Requiere Bearer Token.
- **Respuesta Exitosa (200):**
  - Devuelve el objeto completo del usuario.

---

### 4. Cambiar Contraseña

- **Endpoint:** `POST /auth/change-password`
- **Descripción:** Permite a un usuario autenticado cambiar su propia contraseña.
- **Autenticación:** Requiere Bearer Token.
- **Request Body:**
  ```json
  {
    "current_password": "tu-contraseña-actual",
    "new_password": "tu-nueva-contraseña-segura"
  }
  ```
- **Respuesta Exitosa (200):**
  - Mensaje de confirmación.

## Endpoints de Emails (`/emails`)

---

### 1. Enviar un Email

- **Endpoint:** `POST /emails/send`
- **Descripción:** Envía un correo electrónico usando `application/json`. Puede ser texto plano, HTML o basado en plantilla.
- **Tipo de Contenido:** `application/json`
- **Request Body:**
  ```json
  {
    "user_id": 3,
    "recipient": "alexisdurangomez588@gmail.com",
    "subject": "Bienvenido",
    "template_name": "welcome.html",
    "template_data": {
      "nombre": "Juan",
      "empresa": "Mi Empresa"
    }
  }
  ```
- **Respuesta Exitosa (201):**
  - Devuelve el registro del email creado, con su estado (`sent`, `failed`).

### 2. Enviar un Email con Formulario

- **Endpoint:** `POST /emails/send/form`
- **Descripción:** Envía un correo electrónico usando `multipart/form-data`. Este endpoint debe usarse cuando se necesita adjuntar un PDF.
- **Tipo de Contenido:** `multipart/form-data`
- **Parámetros (Form-Data):**
  - `user_id` (int, requerido): ID del usuario que envía.
  - `recipient` (str, requerido): Email del destinatario.
  - `subject` (str, requerido): Asunto.
  - `body` (str, opcional): Cuerpo en texto plano.
  - `html_body` (str, opcional): Cuerpo en HTML.
  - `template_name` (str, opcional): Nombre de la plantilla (`welcome.html`, etc.).
  - `template_data` (str, opcional): String JSON con variables para la plantilla.
  - `pdf_attachment` (File, opcional): Archivo PDF a adjuntar.
- **Respuesta Exitosa (201):**
  - Devuelve el registro del email creado, con su estado (`sent`, `failed`).

---

### 3. Obtener Lista de Emails

- **Endpoint:** `GET /emails/`
- **Descripción:** Devuelve una lista paginada de todos los emails enviados en el sistema.
- **Query Parameters:**
  - `page` (int, opcional, default: 1): Número de página.
  - `page_size` (int, opcional, default: 10): Items por página.
- **Respuesta Exitosa (200):**
  - Un objeto con `emails`, `total`, `page` y `page_size`.

---

### 4. Obtener un Email Específico

- **Endpoint:** `GET /emails/{email_id}`
- **Descripción:** Devuelve los detalles de un email por su ID.
- **Respuesta Exitosa (200):**
  - El objeto completo del email.

---

### 5. Eliminar un Email

- **Endpoint:** `DELETE /emails/{email_id}`
- **Descripción:** Elimina el registro de un email de la base de datos.
- **Respuesta Exitosa (200):**
  - Mensaje de confirmación.

## Endpoints de Usuarios (`/users`)

---

### 1. Verificar Email

- **Endpoint:** `GET /users/verify-email`
- **Descripción:** Verifica la dirección de correo de un usuario a través del token que recibió al registrarse.
- **Query Parameters:**
  - `token` (str, requerido): Token de verificación.
- **Respuesta Exitosa (200):**
  - Mensaje de confirmación.

---

### 2. Obtener Bandeja de Salida Personal

- **Endpoint:** `GET /users/me/inbox`
- **Descripción:** Devuelve la lista de emails enviados por el usuario autenticado.
- **Autenticación:** Requiere Bearer Token.
- **Query Parameters:**
  - `page` (int, opcional, default: 1).
  - `page_size` (int, opcional, default: 10).
- **Respuesta Exitosa (200):**
  - Lista paginada de los emails del usuario.

---

### 3. Reenviar un Email

- **Endpoint:** `POST /users/me/inbox/{email_id}/resend`
- **Descripción:** Reenvía un email que el usuario envió previamente.
- **Autenticación:** Requiere Bearer Token.
- **Respuesta Exitosa (201):**
  - El nuevo registro del email reenviado.

---

### 4. Enviar Email con Plantilla

- **Endpoint:** `POST /users/me/send-template`
- **Descripción:** Envía un email utilizando una de las plantillas predefinidas.
- **Autenticación:** Requiere Bearer Token.
- **Request Body:**
  ```json
  {
    "recipient": "cliente@example.com",
    "subject": "Asunto con Plantilla",
    "template_name": "welcome.html",
    "template_data": {
      "nombre": "Juan Pérez",
      "empresa": "Mi Empresa"
    }
  }
  ```
- **Respuesta Exitosa (201):**
  - El registro del email enviado.

---

## Endpoints de Administrador (`/users/admin`)

**Nota:** Todas las rutas de administrador requieren un Bearer Token de un usuario con rol `admin`.

---

### 1. Listar Todos los Usuarios

- **Endpoint:** `GET /users/admin/all`
- **Descripción:** Devuelve una lista paginada de todos los usuarios del sistema.

---

### 2. Listar Usuarios Pendientes

- **Endpoint:** `GET /users/admin/pending`
- **Descripción:** Devuelve una lista de usuarios cuyo estado es `PENDING` y esperan aprobación.

---

### 3. Obtener Estadísticas

- **Endpoint:** `GET /users/admin/stats`
- **Descripción:** Retorna estadísticas sobre el número de usuarios (total, activos, pendientes).

---

### 4. Aprobar Usuario

- **Endpoint:** `POST /users/admin/{user_id}/approve`
- **Descripción:** Cambia el estado de un usuario de `PENDING` a `ACTIVE` y le notifica por correo.

---

### 5. Cambiar Estado de Usuario

- **Endpoint:** `PATCH /users/admin/{user_id}/status`
- **Descripción:** Permite cambiar el estado de un usuario a `active`, `pending`, `blocked` o `deleted`.
- **Request Body:**
  ```json
  {
    "status": "blocked"
  }
  ```

---

### 6. Actualizar Usuario

- **Endpoint:** `PUT /users/admin/{user_id}`
- **Descripción:** Actualiza los datos de un usuario (nombre, email, rol).

---

### 7. Eliminar Usuario

- **Endpoint:** `DELETE /users/admin/{user_id}`
- **Descripción:** Realiza un borrado lógico del usuario, cambiando su estado a `deleted`.
