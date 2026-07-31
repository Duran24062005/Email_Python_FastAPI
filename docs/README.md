# Indice de documentacion

> Punto de entrada para navegar la documentacion del proyecto como vault de Obsidian.
> Este indice no reemplaza los documentos existentes: los conecta por dominio, capa y flujo.

## Entrada rapida para Obsidian

- [[docs/obsidian-map|Mapa grafico y relacional de documentacion]]
- [Indice de PRDs](../prds/README.md)
- [README principal](../README.md)

Para ver las relaciones de forma grafica:

1. Abrir la raiz del repositorio como vault en Obsidian.
2. Abrir [[docs/obsidian-map|Mapa grafico y relacional de documentacion]].
3. Usar `Open local graph` o `Graph view` con profundidad `2`.

## Documentos base

| Documento | Rol |
|---|---|
| [[docs/System_Artifact|System Artifact]] | Vision completa del sistema, actores, modulos, datos, seguridad, despliegue y decisiones. |
| [[docs/architecture|Arquitectura]] | Arquitectura en capas, SOLID, inyeccion de dependencias y flujo de datos. |
| [[docs/API_REFERENCE|API Reference]] | Referencia principal y detallada de endpoints, schemas y errores. |
| [[docs/api_docs|API docs resumida]] | Guia API mas compacta, util como lectura rapida. |

## Operacion e infraestructura

| Documento | Relacion principal |
|---|---|
| [[docs/docker|Docker]] | Ejecucion local con contenedores, PostgreSQL y flujo recomendado con migraciones. |
| [[docs/alembic|Alembic]] | Fuente versionada para evolucionar el esquema PostgreSQL. |
| [[docs/TROUBLESHOOTING|Troubleshooting]] | Diagnostico de errores comunes de base de datos, SMTP, plantillas y entorno. |
| [[docs/gitflow|GitFlow]] | Flujo de ramas, releases, hotfixes y convencion de commits. |

## Mantenimiento documental

| Documento | Uso |
|---|---|
| [[docs/docstring_guide|Docstrings]] | Guia de docstrings para FastAPI y Swagger. |
| [[docs/STYLE_DOSCTRINGS_GUIDE|Estandar de docstrings]] | Plantilla y formato esperado para documentar modulos y endpoints. |

## Mapas por dominio

### Autenticacion y usuarios

- PRDs principales: [[prds/002-user-registration|002 - Registro]], [[prds/003-user-login|003 - Login]], [[prds/004-change-password|004 - Cambio de contrasena]], [[prds/005-email-verification|005 - Verificacion]], [[prds/006-auth-me|006 - Auth me]], [[prds/007-user-profile|007 - Perfil]], [[prds/011-save-email-key|011 - Clave SMTP personal]].
- Documentos relacionados: [[docs/API_REFERENCE|API Reference]], [[docs/System_Artifact|System Artifact]], [[docs/architecture|Arquitectura]].
- Codigo relacionado: `app/routes/auth_routes.py`, `app/routes/user_routes.py`, `app/services/auth_service.py`, `app/services/user_service.py`, `app/models/user_models.py`.

### Administracion de usuarios

- PRDs principales: [[prds/012-admin-list-users|012 - Listar usuarios]], [[prds/013-admin-list-pending-users|013 - Pendientes]], [[prds/014-admin-user-stats|014 - Estadisticas]], [[prds/015-admin-get-user|015 - Consultar usuario]], [[prds/016-admin-approve-user|016 - Aprobar]], [[prds/017-admin-change-user-status|017 - Cambiar estado]], [[prds/018-admin-update-user|018 - Actualizar]], [[prds/019-admin-delete-user|019 - Eliminar]].
- Documentos relacionados: [[docs/API_REFERENCE|API Reference]], [[docs/System_Artifact|System Artifact]], [[docs/architecture|Arquitectura]].
- Codigo relacionado: `app/routes/user_routes.py`, `app/middlewares/role_middleware.py`, `app/services/user_service.py`, `app/repositories/user_repository.py`.

### Emails y plantillas

- PRDs principales: [[prds/001-pdf-attachments|001 - Adjuntos PDF]], [[prds/008-user-inbox|008 - Bandeja]], [[prds/009-resend-email|009 - Reenvio]], [[prds/010-send-template-email|010 - Plantillas]], [[prds/020-list-emails|020 - Listar emails]], [[prds/021-get-email-detail|021 - Detalle]], [[prds/022-send-email|022 - Envio]], [[prds/023-update-email-status|023 - Actualizar estado]], [[prds/024-delete-email|024 - Eliminar]], [[prds/025-email-send-form-endpoint|025 - JSON/Form]].
- Documentos relacionados: [[docs/API_REFERENCE|API Reference]], [[docs/System_Artifact|System Artifact]], [[docs/architecture|Arquitectura]], [[docs/TROUBLESHOOTING|Troubleshooting]].
- Codigo relacionado: `app/routes/email_routes.py`, `app/controllers/emails_controller.py`, `app/services/email_services.py`, `app/repositories/email_repository.py`, `app/utils/smtp_email_sender.py`, `app/utils/template_engine.py`, `app/templates/`.

### Base de datos y migraciones

- PRD principal: [[prds/026-alembic-schema-alignment|026 - Alembic y alineacion de esquema]].
- Documentos relacionados: [[docs/alembic|Alembic]], [[docs/docker|Docker]], [[docs/TROUBLESHOOTING|Troubleshooting]], [[docs/System_Artifact|System Artifact]].
- Codigo/artefactos relacionados: `alembic/`, `alembic.ini`, `database.sql`, `app/config/database/`, `app/models/`.

## Reglas de actualizacion

- Si se agrega o cambia un endpoint, actualizar [[docs/API_REFERENCE|API Reference]] y el PRD correspondiente.
- Si el cambio afecta reglas de negocio, contratos HTTP o flujo funcional, agregar o actualizar un PRD en `prds/`.
- Si cambia el esquema de datos, actualizar [[docs/alembic|Alembic]], [[prds/026-alembic-schema-alignment|PRD 026]] si aplica, y revisar `database.sql`.
- Si cambia la forma de ejecutar, desplegar o diagnosticar el sistema, actualizar [[docs/docker|Docker]] o [[docs/TROUBLESHOOTING|Troubleshooting]].
- Si se agrega un documento nuevo, enlazarlo desde este indice y desde [[docs/obsidian-map|Mapa grafico y relacional de documentacion]].
