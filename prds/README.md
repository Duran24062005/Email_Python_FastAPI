# Indice de PRDs

> Indice funcional de los PRDs del proyecto. Esta agrupacion esta pensada para que Obsidian muestre clusters por dominio y para que los cambios futuros tengan trazabilidad.

## Mapas relacionados

- [[docs/obsidian-map|Mapa grafico y relacional de documentacion]]
- [[docs/README|Indice de documentacion]]
- [[docs/API_REFERENCE|API Reference]]
- [[docs/System_Artifact|System Artifact]]

## Auth y usuario propio

| PRD | Endpoint o flujo | Relaciones principales |
|---|---|---|
| [[prds/002-user-registration|002 - Registro de Usuario]] | `POST /api/auth/register` | [[prds/005-email-verification|005]], [[prds/003-user-login|003]], [[docs/API_REFERENCE|API]] |
| [[prds/003-user-login|003 - Inicio de Sesion de Usuario]] | `POST /api/auth/login` | [[prds/002-user-registration|002]], [[prds/004-change-password|004]], [[prds/006-auth-me|006]] |
| [[prds/004-change-password|004 - Cambio de Contrasena]] | `POST /api/auth/change-password` | [[prds/003-user-login|003]], [[docs/API_REFERENCE|API]] |
| [[prds/005-email-verification|005 - Verificacion de Email]] | `GET /api/users/verify-email` | [[prds/002-user-registration|002]], [[docs/System_Artifact|System]] |
| [[prds/006-auth-me|006 - Perfil Autenticado en Auth]] | `GET /api/auth/me` | [[prds/003-user-login|003]], [[prds/007-user-profile|007]] |
| [[prds/007-user-profile|007 - Perfil Propio de Usuario]] | `GET /api/users/me` | [[prds/006-auth-me|006]], [[docs/API_REFERENCE|API]] |
| [[prds/011-save-email-key|011 - Guardado de Clave SMTP Personal]] | `PUT /api/users/me/email-key` | [[prds/010-send-template-email|010]], [[prds/022-send-email|022]] |

## Administracion de usuarios

| PRD | Endpoint o flujo | Relaciones principales |
|---|---|---|
| [[prds/012-admin-list-users|012 - Listado General de Usuarios]] | `GET /api/users/admin/all` | [[prds/015-admin-get-user|015]], [[prds/014-admin-user-stats|014]] |
| [[prds/013-admin-list-pending-users|013 - Listado de Usuarios Pendientes]] | `GET /api/users/admin/pending` | [[prds/016-admin-approve-user|016]], [[prds/014-admin-user-stats|014]] |
| [[prds/014-admin-user-stats|014 - Estadisticas de Usuarios]] | `GET /api/users/admin/stats` | [[prds/012-admin-list-users|012]], [[prds/013-admin-list-pending-users|013]] |
| [[prds/015-admin-get-user|015 - Consulta de Usuario por ID]] | `GET /api/users/admin/{user_id}` | [[prds/012-admin-list-users|012]], [[prds/018-admin-update-user|018]] |
| [[prds/016-admin-approve-user|016 - Aprobacion de Usuario]] | `POST /api/users/admin/{user_id}/approve` | [[prds/013-admin-list-pending-users|013]], [[prds/017-admin-change-user-status|017]] |
| [[prds/017-admin-change-user-status|017 - Cambio de Estado de Usuario]] | `PATCH /api/users/admin/{user_id}/status` | [[prds/016-admin-approve-user|016]], [[prds/019-admin-delete-user|019]] |
| [[prds/018-admin-update-user|018 - Actualizacion Administrativa de Usuario]] | `PUT /api/users/admin/{user_id}` | [[prds/015-admin-get-user|015]], [[prds/017-admin-change-user-status|017]] |
| [[prds/019-admin-delete-user|019 - Eliminacion de Usuario]] | `DELETE /api/users/admin/{user_id}` | [[prds/012-admin-list-users|012]], [[prds/017-admin-change-user-status|017]] |

## Emails, plantillas y trazabilidad

| PRD | Endpoint o flujo | Relaciones principales |
|---|---|---|
| [[prds/001-pdf-attachments|001 - Soporte para Archivos Adjuntos en PDF]] | Adjuntos en envio | [[prds/022-send-email|022]], [[prds/025-email-send-form-endpoint|025]] |
| [[prds/008-user-inbox|008 - Bandeja de Salida del Usuario]] | `GET /api/users/me/inbox` | [[prds/009-resend-email|009]], [[prds/022-send-email|022]] |
| [[prds/009-resend-email|009 - Reenvio de Email]] | `POST /api/users/me/inbox/{email_id}/resend` | [[prds/008-user-inbox|008]], [[prds/021-get-email-detail|021]] |
| [[prds/010-send-template-email|010 - Envio de Email con Plantilla]] | `POST /api/users/me/send-template` | [[prds/011-save-email-key|011]], [[prds/022-send-email|022]] |
| [[prds/020-list-emails|020 - Listado Global de Emails]] | `GET /emails/` | [[prds/021-get-email-detail|021]], [[docs/API_REFERENCE|API]] |
| [[prds/021-get-email-detail|021 - Consulta de Email por ID]] | `GET /emails/{email_id}` | [[prds/020-list-emails|020]], [[prds/023-update-email-status|023]], [[prds/024-delete-email|024]] |
| [[prds/022-send-email|022 - Envio de Email]] | `POST /emails/send` | [[prds/001-pdf-attachments|001]], [[prds/010-send-template-email|010]], [[prds/025-email-send-form-endpoint|025]] |
| [[prds/023-update-email-status|023 - Actualizacion de Registro de Email]] | `PUT /emails/update/{email_id}` | [[prds/021-get-email-detail|021]], [[prds/020-list-emails|020]] |
| [[prds/024-delete-email|024 - Eliminacion de Email]] | `DELETE /emails/{email_id}` | [[prds/021-get-email-detail|021]], [[prds/020-list-emails|020]] |
| [[prds/025-email-send-form-endpoint|025 - Separacion de Envio JSON y Formulario]] | `POST /emails/send` y `POST /emails/send/form` | [[prds/022-send-email|022]], [[prds/001-pdf-attachments|001]] |

## Base de datos, migraciones e infraestructura

| PRD | Endpoint o flujo | Relaciones principales |
|---|---|---|
| [[prds/026-alembic-schema-alignment|026 - Alembic y alineacion de esquema]] | Migraciones y contrato de base de datos | [[docs/alembic|Alembic]], [[docs/docker|Docker]], [[docs/TROUBLESHOOTING|Troubleshooting]], [[docs/System_Artifact|System]] |

## Secuencias funcionales

- Onboarding: [[prds/002-user-registration|002 Registro]] -> [[prds/005-email-verification|005 Verificacion]] -> [[prds/003-user-login|003 Login]] -> [[prds/006-auth-me|006 Auth me]].
- Gestion personal: [[prds/007-user-profile|007 Perfil]] -> [[prds/011-save-email-key|011 Clave SMTP]] -> [[prds/010-send-template-email|010 Plantillas]].
- Envio y consulta de emails: [[prds/022-send-email|022 Envio]] -> [[prds/020-list-emails|020 Listado]] -> [[prds/021-get-email-detail|021 Detalle]] -> [[prds/023-update-email-status|023 Estado]] / [[prds/024-delete-email|024 Eliminar]].
- Bandeja de usuario: [[prds/008-user-inbox|008 Bandeja]] -> [[prds/009-resend-email|009 Reenvio]].
- Administracion: [[prds/012-admin-list-users|012 Listar]] -> [[prds/013-admin-list-pending-users|013 Pendientes]] -> [[prds/016-admin-approve-user|016 Aprobar]] -> [[prds/017-admin-change-user-status|017 Estado]] -> [[prds/018-admin-update-user|018 Actualizar]] / [[prds/019-admin-delete-user|019 Eliminar]].

## Regla de mantenimiento

Cuando se agregue un PRD nuevo:

1. Ubicarlo en el dominio correcto dentro de este indice.
2. Enlazarlo desde [[docs/obsidian-map|Mapa grafico y relacional de documentacion]].
3. Revisar si corresponde actualizar [[docs/API_REFERENCE|API Reference]], [[docs/System_Artifact|System Artifact]], [[docs/architecture|Arquitectura]] u operacion.
