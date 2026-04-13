# 📧 Email Python FastAPI — System Artifact

> Documento principal del sistema. Describe el propósito, arquitectura, módulos, flujos de datos y decisiones de diseño basándose en el código fuente real del proyecto.

---

## 1. Descripción General

**Email Python FastAPI** es una API REST construida con Python 3.12 y FastAPI que provee servicios de gestión y envío de correos electrónicos con plantillas HTML, autenticación JWT, verificación de email, y un sistema completo de gestión de usuarios con roles (general y administrador).

### Objetivo

Proveer un backend modular, extensible y bien estructurado para el envío de comunicaciones por email, que pueda integrarse como servicio interno en cualquier producto que requiera envíos transaccionales o de notificación.

### Casos de Uso Cubiertos

| Actor | Acciones disponibles |
|---|---|
| **Usuario general** | Registro, login, ver perfil, bandeja de salida, reenviar emails, enviar con plantillas HTML, guardar clave SMTP personal, verificar email |
| **Administrador** | Listar todos los usuarios, ver usuarios pendientes, aprobar cuentas, cambiar estado, actualizar datos, eliminar, ver estadísticas |
| **Sistema** | Envío automático de email de verificación al registrarse, notificación cuando una cuenta es aprobada |

---

## 2. Stack Tecnológico

| Capa | Tecnología | Versión |
|---|---|---|
| Framework web | FastAPI | 0.121.3 |
| Servidor ASGI | Uvicorn | 0.38.0 |
| Lenguaje | Python | 3.12 |
| Base de datos | PostgreSQL | 16 |
| ORM | SQLAlchemy | 2.0.44 |
| Autenticación | PyJWT | 2.11.0 |
| Hash de contraseñas | bcrypt | 5.0.0 |
| Validación de emails | email-validator | 2.2.0 |
| Motor de plantillas | Jinja2 | 3.1.4 |
| Validación de datos | Pydantic | 2.12.4 |
| Variables de entorno | python-dotenv | 1.2.1 |
| Contenedores | Docker + Docker Compose | — |
| Despliegue serverless | Vercel | — |

---

## 3. Arquitectura del Sistema

El proyecto implementa una **arquitectura en capas** con separación estricta de responsabilidades. Cada capa depende únicamente de la inmediatamente inferior.

```
┌──────────────────────────────────────────────────────────┐
│                        HTTP Client                       │
└────────────────────────┬─────────────────────────────────┘
                         │  HTTP Request
┌────────────────────────▼─────────────────────────────────┐
│                    FastAPI Routes                        │
│         auth_routes / user_routes / email_routes         │
│   Define endpoints · Docstrings → Swagger UI · Depends() │
└────────────────────────┬─────────────────────────────────┘
                         │  Depends(get_current_active_user)
┌────────────────────────▼─────────────────────────────────┐
│                     Middlewares                          │
│  auth_middleware (JWT → User) · role_middleware (ADMIN)  │
└────────────────────────┬─────────────────────────────────┘
                         │  Controller inyectado via Depends()
┌────────────────────────▼─────────────────────────────────┐
│                     Controllers                          │
│    AuthController · UserController · EmailController     │
│  Captura excepciones de dominio · valida paginación      │
└────────────────────────┬─────────────────────────────────┘
                         │  Llama métodos de servicio
┌────────────────────────▼─────────────────────────────────┐
│                      Services                            │
│       AuthService · UserService · EmailService           │
│  Lógica de negocio · orquestación · reglas de dominio    │
└──────┬──────────────┬──────────────┬─────────────────────┘
       │              │              │
  ┌────▼────┐   ┌─────▼────┐  ┌─────▼──────────────────┐
  │UserRepo │   │EmailRepo │  │  IEmailSender           │
  │(SQLAlch)│   │(SQLAlch) │  │  SMTPEmailSender/Mock   │
  └────┬────┘   └─────┬────┘  │  ITemplateEngine        │
       │              │        │  Jinja2/Simple          │
  ┌────▼──────────────▼──────┐ └────────────────────────┘
  │         PostgreSQL        │
  │    tabla users + emails   │
  └───────────────────────────┘
```

### Wiring de Dependencias (`dependencies.py`)

Todo el ensamblaje de objetos ocurre en un único archivo. Los servicios no saben qué implementación concreta reciben.

```
get_db() → SessionLocal
  └─ get_email_repository(db) → EmailRepository
  └─ get_user_repository(db)  → UserRepository

get_email_sender()    → SMTPEmailSender (ENVIRONMENT=production)
                      → MockEmailSender (ENVIRONMENT=development)
get_template_engine() → Jinja2TemplateEngine("templates/")

get_email_service(email_repo, sender, template_engine) → EmailService
get_auth_service(user_repo, sender, template_engine)   → AuthService
get_user_service(user_repo, email_repo, sender, template_engine) → UserService

get_email_controller(email_service) → EmailController
get_auth_controller(auth_service)   → AuthController
get_user_controller(user_service)   → UserController
```

---

## 4. Estructura de Archivos

```
Email_Python_FastAPI/
│
├── config/
│   ├── config.py                   # app_config y database_config desde .env
│   └── database/
│       ├── base.py                 # Base declarativa compartida de SQLAlchemy
│       └── connection.py           # Engine, SessionLocal, get_db(), check_db_connection()
│
├── core/
│   ├── exceptions.py               # DomainError, EmailAlreadyExists, WeakPassword
│   └── security.py                 # hash_password(), verify_password(),
│                                   # create_access_token(), decode_access_token()
│
├── interfaces/
│   ├── email_interfaces.py         # IEmailRepository, IEmailSender, ITemplateEngine (ABC)
│   └── user_interfaces.py          # IUserRepository (ABC)
│
├── models/
│   ├── email_model.py              # Modelo Email (SQLAlchemy), EmailStatus enum
│   └── user_models.py              # Modelo User (SQLAlchemy), UserStatus enum, UserRole enum
│
├── schemas/
│   ├── email_schema.py             # EmailCreate, EmailResponse, EmailUpdate, EmailList,
│   │                               # SendWithTemplateRequest
│   └── user_schemas.py             # UserCreate, UserUpdate, UserResponse, UserList,
│                                   # LoginRequest, TokenResponse, ChangePasswordRequest,
│                                   # ChangeStatusRequest, SaveEmailKeyRequest
│
├── repositories/
│   ├── email_repository.py         # CRUD + get_by_user_id() + count_by_user() + update_status()
│   ├── user_repository.py          # CRUD + get_by_email() + get_pending_users() +
│   │                               # update_status() + update_email_key() +
│   │                               # set_email_verified() + update_last_login() + update_password()
│   └── send_email.py               # SendEmailRepository (auxiliar, sin uso activo)
│
├── services/
│   ├── auth_service.py             # register(), login(), change_password(),
│   │                               # _send_verification_email()
│   ├── email_services.py           # send_email(), get_email(), get_all_emails(),
│   │                               # update_email(), delete_email()
│   └── user_service.py             # get_my_profile(), get_my_inbox(), resend_email(),
│                                   # send_email_with_template(), save_email_key(),
│                                   # verify_email_token(), get_all_users(), approve_user(),
│                                   # change_user_status(), update_user(), delete_user(), get_stats()
│
├── controllers/
│   ├── auth_controller.py          # HTTP → AuthService, mapeo DomainError → HTTPException
│   ├── emails_controller.py        # HTTP → EmailService, validación de paginación
│   └── user_controller.py          # HTTP → UserService, validación de parámetros
│
├── middlewares/
│   ├── auth_middleware.py          # get_current_user(), get_current_active_user()
│   ├── role_middleware.py          # require_admin()
│   └── cors.py                     # CORSMiddleware (allow_origins=["*"])
│
├── routes/
│   ├── auth_routes.py              # /api/auth: register, login, me, change-password
│   ├── user_routes.py              # /api/users: verify-email, /me/*, /admin/*
│   └── email_routes.py             # /emails: CRUD + send
│
├── utils/
│   ├── smtp_email_sender.py        # SMTPEmailSender (SSL/TLS) + MockEmailSender
│   └── template_engine.py          # Jinja2TemplateEngine + SimpleTemplateEngine
│
├── templates/                      # Plantillas HTML Jinja2
│   ├── welcome.html
│   ├── welcome_educonnect.html
│   ├── account_approved.html
│   └── my_website.html
│
├── static/                         # Archivos estáticos servidos en /public
│   ├── index.html                  # Landing page con documentación visual
│   ├── js/script.js
│   └── styles/styles.css
│
├── docs/                           # Documentación del proyecto
│   ├── SYSTEM_ARTIFACT.md          # ← Este documento
│   ├── API_REFERENCE.md            # Referencia completa de endpoints
│   ├── architecture.md             # Guía SOLID y diagramas (ACTUALIZADO)
│   ├── TROUBLESHOOTING.md          # Guía de resolución de problemas
│   ├── STYLE_DOCSTRINGS_GUIDE.md   # Estándar de docstrings para Swagger
│   ├── docstring_guide.md          # Tutorial de docstrings en FastAPI
│   └── gitflow.md                  # Guía completa de GitFlow
│
├── dependencies.py                 # Wiring de inyección de dependencias
├── main.py                         # Punto de entrada: FastAPI app, routers, startup
├── database.sql                    # Bootstrap completo del esquema para entornos nuevos
├── init_database.py                # Script Python para crear la DB y ejecutar Alembic
├── requirements.txt                # Dependencias con versiones fijadas
├── Dockerfile                      # python:3.12-slim + gcc + libpq-dev
├── docker-compose.yml              # Servicios: email-api + postgres:16-alpine
├── vercel.json                     # Despliegue serverless en Vercel
├── .env.example                    # Plantilla de variables de entorno
├── .gitignore
├── .dockerignore
└── .vercelignore
```

---

## 5. Modelos de Datos

### Tabla `users`

Definida en `models/user_models.py`:

| Columna | Tipo SQLAlchemy | Descripción |
|---|---|---|
| `id` | `Integer PK autoincrement` | Identificador único |
| `name` | `String(255) index` | Nombre completo |
| `email` | `String(255) unique index` | Email del usuario |
| `hash_password` | `String(255)` | Contraseña hasheada con bcrypt |
| `email_key` | `String(255) nullable index` | Clave SMTP personal del usuario |
| `status` | `Enum(UserStatus)` | Estado de la cuenta |
| `role` | `Enum(UserRole)` | Rol del usuario |
| `email_verify` | `Boolean nullable` | Si el email fue verificado |
| `last_login` | `DateTime nullable` | Último inicio de sesión |
| `created_at` | `DateTime default=utcnow` | Fecha de creación |
| `updated_at` | `DateTime onupdate=utcnow` | Última modificación |

**Enums:**

| Enum Python | Valor en BD |
|---|---|
| `UserStatus.PENDING` | `"pending"` |
| `UserStatus.ACTIVE` | `"active"` |
| `UserStatus.UNACTIVE` | `"deleted"` ⚠️ |
| `UserStatus.BLOCKED` | `"blocked"` |
| `UserRole.ADMIN` | `"admin"` |
| `UserRole.GENERAL` | `"general"` |

> ⚠️ **Naming inconsistente:** `UserStatus.UNACTIVE` tiene el valor de string `"deleted"`. El miembro Python se llama `UNACTIVE` pero representa un usuario eliminado.

### Tabla `emails`

Definida en `models/email_model.py`:

| Columna | Tipo SQLAlchemy | Descripción |
|---|---|---|
| `id` | `Integer PK autoincrement` | Identificador único |
| `user_id` | `Integer FK(users.id)` | Usuario propietario |
| `recipient` | `String(255) index` | Email del destinatario |
| `subject` | `String(500)` | Asunto del email |
| `body` | `Text nullable` | Cuerpo en texto plano |
| `html_body` | `Text nullable` | Cuerpo en HTML |
| `status` | `Enum(EmailStatus)` | Estado del envío |
| `error_message` | `Text nullable` | Detalle del error (si falló) |
| `sent_at` | `DateTime nullable` | Timestamp de envío exitoso |
| `created_at` | `DateTime default=utcnow` | Fecha de creación |
| `updated_at` | `DateTime onupdate=utcnow` | Última modificación |

**Enum `EmailStatus`:** `PENDING="pending"`, `SENT="sent"`, `FAILED="failed"`

### Relación

```
users (1) ──── emails (N)
  User.emails ←back_populates→ Email.user
```

---

## 6. Seguridad

### JWT

- Librería: `PyJWT 2.11.0`
- Algoritmo: variable `ALGORITHM` en `.env` (recomendado: `HS256`)
- Firma: `SECRET_KEY` desde `.env`
- Expiración: `ACCESS_TOKEN_EXPIRE_MINUTES` (convertido a `int()` en `core/security.py`)

**Token de acceso — payload:**
```json
{ "sub": "<user_id>", "exp": <timestamp>, "iat": <timestamp> }
```

**Token de verificación de email — payload:**
```json
{ "sub": "<user_id>", "purpose": "email_verification", "exp": <timestamp>, "iat": <timestamp> }
```

El campo `purpose` evita que un token de acceso normal pueda usarse para verificar un email.

### Hashing de Contraseñas

- Librería: `bcrypt 5.0.0`
- Límite de 72 bytes validado en dos niveles: schema Pydantic (`@field_validator`) y `core/security.py`
- Si la contraseña excede 72 bytes, `verify_password()` retorna `False` directamente sin llamar a bcrypt

### Flujo de Autenticación

```
Ruta pública         → sin middleware
Ruta de usuario      → Depends(get_current_active_user)
                         └─ Depends(get_current_user)
                              └─ HTTPBearer extrae el token del header
                              └─ decode_access_token() valida firma y exp
                              └─ UserRepository.get_by_id(sub)
                         └─ verifica status == ACTIVE → 403 si no
Ruta de admin        → Depends(require_admin)
                         └─ Depends(get_current_active_user) (heredado)
                         └─ verifica role == ADMIN → 403 si no
```

### CORS

`middlewares/cors.py` configura `allow_origins=["*"]`. Adecuado para desarrollo, debe restringirse en producción.

---

## 7. Flujos Principales

### 7.1 Registro y Verificación de Email

```
POST /api/auth/register { name, email, password }
  │
  ├─ AuthController.register()
  │    ├─ EmailAlreadyExists → 409
  │    ├─ WeakPassword → 422
  │    └─ Exception → 500
  │
  └─ AuthService.register()
       ├─ get_by_email() → verifica unicidad
       ├─ hash_password() → bcrypt
       ├─ create_with_hash() → crea user (status=ACTIVE, email_verify=False)
       └─ _send_verification_email(user_id, email, name)
            ├─ create_access_token({sub, purpose="email_verification"}, expires=24h)
            ├─ Jinja2.render("welcome_educonnect.html", {nombre, empresa, link_accion})
            └─ IEmailSender.send()   ← fallo silencioso, no bloquea el registro

GET /api/users/verify-email?token=<JWT>
  └─ UserService.verify_email_token()
       ├─ decode_access_token() → ExpiredSignatureError → 400
       ├─ valida purpose == "email_verification" → 400 si no
       ├─ get_by_id(sub) → 404 si no existe
       ├─ si ya verificado → retorna mensaje informativo
       └─ set_email_verified() → email_verify=True
```

### 7.2 Login

```
POST /api/auth/login { email, password }
  └─ AuthService.login()
       ├─ get_by_email() → auth error si no existe
       ├─ verify_password() → auth error si no coincide
       ├─ BLOCKED → 403
       ├─ status != ACTIVE → 403 ("pendiente de activación")
       ├─ update_last_login()
       └─ create_access_token({sub: user_id})
            └─ retorna TokenResponse { access_token, token_type, expires_in: 1800, user }
```

### 7.3 Envío de Email con Plantilla

```
POST /api/users/me/send-template
  Headers: Authorization: Bearer <token>
  Body: { recipient, subject, template_name, template_data }
  │
  ├─ auth_middleware → decode JWT → get_current_active_user()
  └─ UserService.send_email_with_template()
       ├─ Jinja2.render(template_name, template_data) → FileNotFoundError → 404
       ├─ EmailRepository.create() → status=PENDING
       ├─ IEmailSender.send(recipient, subject, body, html_body)
       └─ EmailRepository.update_status(SENT | FAILED)
```

### 7.4 Aprobación de Usuario (Admin)

```
POST /api/users/admin/{user_id}/approve
  Headers: Authorization: Bearer <admin_token>
  │
  ├─ role_middleware → verifica role == ADMIN → 403 si no
  └─ UserService.approve_user()
       ├─ get_by_id() → 404 si no existe
       ├─ status == ACTIVE → 409 ya activo
       ├─ update_status(ACTIVE)
       └─ IEmailSender.send() con account_approved.html ← fallo silencioso
```

### 7.5 Reenvío de Email

```
POST /api/users/me/inbox/{email_id}/resend
  └─ UserService.resend_email(user_id, email_id)
       ├─ get_by_id() → 404 si no existe
       ├─ email.user_id != user_id → 403
       ├─ EmailRepository.create() → nuevo registro con mismo contenido
       └─ IEmailSender.send() → update_status(SENT | FAILED)
```

---

## 8. Plantillas HTML (Jinja2)

Ubicadas en `templates/`, renderizadas por `Jinja2TemplateEngine` con `autoescape=True` (protección XSS).

| Archivo | Propósito | Variables requeridas | Variables opcionales |
|---|---|---|---|
| `welcome.html` | Bienvenida genérica | `nombre`, `empresa` | `mensaje_adicional`, `link_accion` (default: makedev URL) |
| `welcome_educonnect.html` | Verificación de email / bienvenida | `nombre`, `empresa` | `mensaje_adicional`, `link_accion` (URL de verificación) |
| `account_approved.html` | Notificación de cuenta aprobada | `nombre`, `empresa`, `role`, `login_link` | — |
| `my_website.html` | Email de bienvenida del sitio personal | `nombre` | — |

`AuthService` usa `welcome_educonnect.html` para la verificación. `UserService.approve_user()` usa `account_approved.html`.

---

## 9. Envío de Emails

### SMTPEmailSender

Lee configuración desde `.env`. La selección del protocolo se determina por el puerto en `dependencies.py`:

```python
port = int(os.getenv("SMTP_PORT", "587"))
use_ssl = (port == 465)   # SMTP_SSL
use_tls = (port == 587)   # STARTTLS
```

Para Gmail se recomienda una **contraseña de aplicación** (no la contraseña normal): Cuenta → Seguridad → Verificación en 2 pasos → Contraseñas de aplicaciones.

### MockEmailSender

Imprime el email en consola. Usado cuando `ENVIRONMENT != "production"`. Implementa `IEmailSender` con la misma firma, permitiendo intercambio transparente (LSP).

---

## 10. Despliegue

### Docker Compose (recomendado)

```bash
cp .env.example .env   # editar con credenciales reales
docker compose up --build
# API: http://localhost:8001
# Swagger UI: http://localhost:8001/
```

| Servicio | Imagen | Puerto | Nota |
|---|---|---|---|
| `email-api` | Dockerfile (python:3.12-slim) | `8001:8001` | Depende de `postgres` (healthcheck) |
| `postgres` | `postgres:16-alpine` | `5432:5432` | Inicializa con `database.sql` y luego puede alinearse con Alembic |

Los volúmenes `./templates`, `./static` y `./uploads` se montan para hot-reload sin rebuild del contenedor.

### Local sin Docker

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # configurar variables
uvicorn main:app --reload --port 8001
```

### Vercel (serverless)

`vercel.json` configura `main.py` como función Python y sirve `/static` directamente. Las variables de entorno se configuran en el dashboard de Vercel. La base de datos debe ser externa (Vercel Postgres, Neon, Supabase, etc.).

### Inicialización de Base de Datos

`main.py` ya no crea tablas al arrancar.

El flujo correcto es:
1. Crear la base de datos si hace falta.
2. Ejecutar `alembic upgrade head`.
3. Iniciar la API.

---

## 11. Principios SOLID — Implementación Real

### S — Single Responsibility

Cada clase tiene una única razón para cambiar. `EmailRepository` solo accede a la BD. `SMTPEmailSender` solo envía por SMTP. `Jinja2TemplateEngine` solo renderiza plantillas. `AuthController` solo mapea excepciones de dominio a HTTP.

### O — Open/Closed

Agregar un proveedor SendGrid no requiere modificar ningún archivo existente: crear `SendGridEmailSender(IEmailSender)` y registrarlo en `dependencies.py`. Lo mismo aplica para nuevos motores de plantillas o repositorios.

### L — Liskov Substitution

`MockEmailSender` reemplaza completamente a `SMTPEmailSender`. Ambos implementan `IEmailSender.send()` con la misma firma y comportamiento observable (retorna `bool`). Los servicios funcionan sin cambios.

### I — Interface Segregation

Interfaces pequeñas y específicas: `IEmailSender` tiene 1 método, `ITemplateEngine` tiene 1 método, `IEmailRepository` tiene 6 métodos cohesivos. Ninguna clase implementa métodos que no necesita.

### D — Dependency Inversion

Los servicios reciben `IEmailSender` e `ITemplateEngine` (interfaces), no implementaciones concretas. El wiring concreto ocurre únicamente en `dependencies.py`.

---

## 12. Decisiones de Diseño

**¿Por qué `AuthService` recibe `IEmailSender` y `ITemplateEngine`?**
Para poder enviar el email de verificación al registrarse sin acoplar `AuthService` a `UserService`. Ambas dependencias son `Optional` para permitir uso sin sender.

**¿Por qué el fallo de email no cancela el registro ni la aprobación?**
Para evitar que problemas de SMTP bloqueen operaciones críticas de negocio. El error se captura con `print()`. En producción debería usarse logging estructurado.

**¿Por qué `email_verify=False` no bloquea el login?**
El registro crea la cuenta en estado `ACTIVE` inmediatamente. La verificación de email es informativa. Si se requiere verificación obligatoria, agregar la comprobación en `AuthService.login()`.

**¿Por qué `get_pending_users()` hace paginación en Python?**
`UserRepository.get_pending_users()` retorna todos los pendientes sin OFFSET/LIMIT en SQL. `UserService` recorta la lista en Python. Es deuda técnica: sería más eficiente paginar en la consulta SQL.

---

## 13. Limitaciones Conocidas y Deuda Técnica

| Área | Limitación | Solución sugerida |
|---|---|---|
| URL de verificación | Hardcodeada como `https://tu-dominio.com` en `auth_service.py` | Leer `BASE_URL` desde `.env` |
| Paginación de pendientes | Carga todos los usuarios pendientes en memoria y recorta en Python | Agregar `OFFSET/LIMIT` en `UserRepository.get_pending_users()` |
| Email key | Se guarda en texto plano en la base de datos | Cifrar con `cryptography.fernet` antes de persistir |
| Logs | Se usan `print()` en lugar de `logging` | Migrar a `logging` con niveles y formato estructurado |
| Tests | No hay tests automatizados | Agregar `pytest` con fixtures usando `MockEmailSender` |
| Rate limiting | Sin protección contra abuso en `/login` ni `/register` | Integrar `slowapi` |
| CORS | `allow_origins=["*"]` activo en producción | Restringir al dominio del cliente |
| Naming inconsistente | `UserStatus.UNACTIVE` tiene valor `"deleted"` | Renombrar a `UserStatus.DELETED` |
| `repositories/send_email.py` | Clase `SendEmailRepository` sin uso activo en el proyecto | Eliminar o integrar correctamente |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Sin valor por defecto en `.env` — lanza `TypeError` si no está definida | Agregar `int(os.getenv(..., "30"))` |

---

## 14. Variables de Entorno

| Variable | Módulo | Descripción | Requerido |
|---|---|---|---|
| `SECRET_KEY` | `core/security.py` | Clave para firmar JWT | ✅ Producción |
| `ALGORITHM` | `core/security.py` | Algoritmo JWT (`HS256`) | ✅ |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `core/security.py` | Vida del token (debe ser int) | ✅ |
| `ENVIRONMENT` | `dependencies.py` | `production` / `development` | ✅ |
| `SMTP_HOST` | `smtp_email_sender.py` | Servidor SMTP | Solo producción |
| `SMTP_PORT` | `smtp_email_sender.py` + `dependencies.py` | Puerto SMTP (587/465) | Solo producción |
| `SMTP_USER` | `smtp_email_sender.py` | Usuario SMTP (email) | Solo producción |
| `SMTP_PASSWORD` | `smtp_email_sender.py` | Contraseña/clave de aplicación SMTP | Solo producción |
| `PGHOST` | `config/config.py` | Host de PostgreSQL | ✅ |
| `PGPORT` | `config/config.py` | Puerto PostgreSQL (default: `5432`) | ✅ |
| `PGUSER` | `config/config.py` | Usuario PostgreSQL | ✅ |
| `PGPASSWORD` | `config/config.py` | Contraseña PostgreSQL | ✅ |
| `PGDATABASE` | `config/config.py` | Nombre de la base de datos | ✅ |
| `PORT` | `config/config.py` | Puerto de la app (default: `8000`) | No |
| `HOST` | `config/config.py` | Host de la app (default: `0.0.0.0`) | No |

---

*Documentado: Febrero 2026 — Email Python FastAPI v1.0.0*
