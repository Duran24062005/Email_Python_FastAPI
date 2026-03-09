# PRD: 020 - Listado Global de Emails

**Fecha:** 2026-03-09

## 1. Resumen

Esta funcionalidad permite consultar la lista paginada de todos los emails registrados en el sistema a traves del modulo `emails`.

## 2. Descripcion de la Funcionalidad

### Endpoint

- **Endpoint:** `GET /emails/`
- **Tipo de Contenido:** `query params`

### Parametros

El endpoint acepta:

- `page` (int, opcional): Numero de pagina. Por defecto `1`.
- `page_size` (int, opcional): Cantidad de items por pagina. Por defecto `10`, maximo `100`.

### Logica de Implementacion

1.  **Ruta (`routes/email_routes.py`):**
    - Expone `GET /emails/`.
    - Valida parametros de paginacion.

2.  **Controlador (`controllers/emails_controller.py`):**
    - Rechaza `page < 1`.
    - Rechaza `page_size < 1` o `page_size > 100`.
    - Delega la consulta al servicio.

3.  **Servicio (`services/email_services.py`):**
    - Obtiene registros paginados.
    - Retorna un `EmailList`.

### Errores Relevantes

- `400`: Parametros de paginacion invalidos.

## 3. Como Usar

Para listar emails, se debe realizar una peticion `GET` al endpoint `/emails/`.

### Ejemplo con `curl`:

```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/emails/?page=1&page_size=10' \
  -H 'accept: application/json'
```

### Uso desde la Documentacion Interactiva de FastAPI

En `/docs`, este endpoint permite navegar el historial completo de registros de email del sistema.

## 4. Impacto

- **Observabilidad operativa:** Facilita revisar actividad global de envios.
- **Soporte a auditoria:** Permite analizar estados y errores de correos registrados.
