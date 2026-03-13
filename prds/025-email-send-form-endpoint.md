# PRD: 025 - Separacion de Envio JSON y Formulario

**Fecha:** 2026-03-13

## 1. Resumen

Se separa el flujo de envio de emails en dos endpoints:

- `POST /emails/send` para solicitudes JSON simples.
- `POST /emails/send/form` para solicitudes `multipart/form-data`, con soporte para adjunto PDF.

El objetivo es evitar ambiguedad en clientes y Swagger, manteniendo una interfaz estable para envio basico y otra especializada para formularios.

## 2. Problema

El endpoint `POST /emails/send` habia sido convertido a `multipart/form-data` para soportar adjuntos PDF. Esto genero dos problemas:

1. Los clientes que enviaban JSON recibian errores `422` por campos faltantes.
2. La documentacion y los ejemplos del schema `EmailCreate` seguian mostrando un body JSON, creando una experiencia inconsistente.

## 3. Solucion

### Endpoint JSON

- **Endpoint:** `POST /emails/send`
- **Tipo de contenido:** `application/json`
- **Uso esperado:** envio basico de emails con texto plano, HTML o plantilla.

Ejemplo:

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

### Endpoint Form

- **Endpoint:** `POST /emails/send/form`
- **Tipo de contenido:** `multipart/form-data`
- **Uso esperado:** envio de emails cuando se necesite cargar un PDF adjunto o consumir la API desde formularios.

Campos:

- `user_id` (int, requerido)
- `recipient` (str, requerido)
- `subject` (str, requerido)
- `body` (str, opcional)
- `html_body` (str, opcional)
- `template_name` (str, opcional)
- `template_data` (str JSON, opcional)
- `pdf_attachment` (File, opcional)

## 4. Criterios de Aceptacion

1. `POST /emails/send` acepta `application/json` y procesa correctamente el payload `EmailCreate`.
2. `POST /emails/send/form` acepta `multipart/form-data` y permite adjuntar un PDF.
3. Ambos endpoints reutilizan la misma logica de negocio de envio.
4. Si `template_data` en `/emails/send/form` no es JSON valido, la API responde `422`.
5. Swagger y la documentacion textual reflejan claramente la diferencia entre ambos contratos.

## 5. Impacto

- Se restaura compatibilidad con clientes JSON.
- Se conserva el soporte de adjuntos sin afectar el endpoint principal.
- Se reduce la confusion en integraciones futuras y en despliegues sobre Vercel.
