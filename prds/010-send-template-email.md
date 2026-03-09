# PRD: 010 - Envio de Email con Plantilla

**Fecha:** 2026-03-09

## 1. Resumen

Esta funcionalidad permite al usuario autenticado enviar un email HTML basado en una plantilla del sistema. El usuario elige la plantilla y provee los datos necesarios para renderizar su contenido.

## 2. Descripcion de la Funcionalidad

### Endpoint

- **Endpoint:** `POST /api/users/me/send-template`
- **Tipo de Contenido:** `application/json` + `Authorization: Bearer`

### Parametros

El endpoint acepta un cuerpo JSON con los siguientes campos:

- `recipient` (str, requerido): Email del destinatario.
- `subject` (str, requerido): Asunto del correo.
- `template_name` (str, requerido): Nombre de la plantilla HTML.
- `template_data` (obj, opcional): Variables a inyectar en la plantilla.

### Logica de Implementacion

1.  **Ruta (`routes/user_routes.py`):**
    - Expone `POST /api/users/me/send-template`.
    - Requiere usuario autenticado y activo.

2.  **Controlador (`controllers/user_controller.py`):**
    - Delega el envio al `UserService`.

3.  **Servicio (`services/user_service.py`):**
    - Renderiza la plantilla seleccionada.
    - Crea un registro del email en la base de datos.
    - Intenta enviar el correo con HTML generado.
    - Actualiza el estado del registro a `sent` o `failed`.

### Errores Relevantes

- `401`: Token invalido, ausente o expirado.
- `403`: Usuario inactivo o bloqueado.
- `404`: Plantilla no encontrada.
- `422`: Fallo de validacion del schema.

## 3. Como Usar

Para enviar un email con plantilla, se debe realizar una peticion `POST` al endpoint `/api/users/me/send-template` utilizando `application/json`.

### Ejemplo con `curl`:

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/users/me/send-template' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer TU_ACCESS_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "recipient": "cliente@example.com",
    "subject": "Bienvenido a la plataforma",
    "template_name": "welcome.html",
    "template_data": {
      "nombre": "Juan Perez",
      "empresa": "Mi Empresa",
      "mensaje_adicional": "Gracias por registrarte"
    }
  }'
```

### Uso desde la Documentacion Interactiva de FastAPI

La documentacion en `/docs` permite capturar el nombre de plantilla y las variables de `template_data` para probar el renderizado y envio.

## 4. Impacto

- **Personalizacion:** Permite generar emails HTML reutilizando plantillas del sistema.
- **Eficiencia operativa:** Centraliza el contenido visual y reduce composicion manual.
