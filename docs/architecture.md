# 🏗️ Arquitectura — Email Python FastAPI

> Este documento describe la arquitectura en capas, los principios SOLID aplicados y los flujos de datos del sistema completo, incluyendo los módulos de autenticación, usuarios y emails agregados en v1.0.

---

## 📊 Diagrama General del Sistema

```
┌──────────────────────────────────────────────────────────┐
│                        HTTP Client                       │
└──────┬───────────────────┬───────────────────────────────┘
       │                   │
  /api/auth/*         /api/users/*          /emails/*
       │                   │                    │
┌──────▼───────────────────▼────────────────────▼──────────┐
│                        main.py                           │
│  FastAPI app · startup(init_db) · CORSMiddleware         │
│  auth_router · user_router · email_router                │
└────────────────────────┬─────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
  ┌──────▼──────┐ ┌──────▼──────┐ ┌─────▼───────┐
  │ auth_routes │ │ user_routes │ │email_routes │
  └──────┬──────┘ └──────┬──────┘ └─────┬───────┘
         │               │               │
    Depends()       Depends()       Depends()
         │               │               │
  ┌──────▼──────┐ ┌──────▼──────┐ ┌─────▼───────────┐
  │auth_middlew │ │role_middlew │ │ (sin auth)       │
  │get_current  │ │require_admin│ │                  │
  │_active_user │ │             │ │                  │
  └──────┬──────┘ └──────┬──────┘ └─────┬───────────┘
         │               │               │
  ┌──────▼──────┐ ┌──────▼──────┐ ┌─────▼───────┐
  │AuthControll │ │UserControll │ │EmailControl │
  └──────┬──────┘ └──────┬──────┘ └─────┬───────┘
         │               │               │
  ┌──────▼──────┐ ┌──────▼──────┐ ┌─────▼───────┐
  │AuthService  │ │UserService  │ │EmailService │
  └──────┬──────┘ └──────┬──────┘ └─────┬───────┘
         │               │               │
    ┌────┴──────────────┬┘        ┌──────┘
    │                   │         │
┌───▼────┐      ┌───────▼──┐  ┌──▼──────────────────┐
│UserRepo│      │EmailRepo │  │  IEmailSender        │
└───┬────┘      └───────┬──┘  │  ITemplateEngine     │
    │                   │     └──────────────────────┘
    └─────────┬─────────┘
        ┌─────▼──────┐
        │ PostgreSQL  │
        │ users+email │
        └────────────┘
```

---

## 🎯 Principios SOLID Aplicados

### 1️⃣ Single Responsibility Principle

**"Una clase debe tener una sola razón para cambiar"**

El sistema separa claramente cada responsabilidad en una clase distinta:

```python
# Cada clase tiene UN único propósito

class UserRepository:
    # Solo lee/escribe en la tabla users
    async def get_by_id(self, user_id: int): ...
    async def update_status(self, user_id: int, status: UserStatus): ...

class SMTPEmailSender:
    # Solo envía emails por SMTP
    async def send(self, recipient, subject, body, html_body): ...

class Jinja2TemplateEngine:
    # Solo renderiza plantillas HTML
    def render(self, template_name, context): ...

class AuthService:
    # Solo gestiona identidad: registro, login, cambio de contraseña
    async def register(self, user_data): ...
    async def login(self, credentials): ...

class UserService:
    # Solo gestiona el ciclo de vida del usuario y sus emails
    async def get_my_inbox(self, user_id, page, page_size): ...
    async def approve_user(self, user_id): ...

class AuthController:
    # Solo traduce DomainError → HTTPException
    async def register(self, user_data) -> UserResponse: ...
```

**Consecuencia:** si cambia el protocolo de envío de email, solo se modifica `SMTPEmailSender`. Si cambia la lógica de aprobación de usuarios, solo se modifica `UserService`.

---

### 2️⃣ Open/Closed Principle

**"Abierto para extensión, cerrado para modificación"**

Las interfaces permiten agregar implementaciones sin tocar el código existente:

```python
# Interfaz base — nunca se modifica
class IEmailSender(ABC):
    @abstractmethod
    async def send(self, recipient, subject, body, html_body=None) -> bool: ...

# ✅ Implementación 1 — existe
class SMTPEmailSender(IEmailSender):
    async def send(self, recipient, subject, body, html_body=None) -> bool:
        # lógica SMTP
        ...

# ✅ Implementación 2 — existe
class MockEmailSender(IEmailSender):
    async def send(self, recipient, subject, body, html_body=None) -> bool:
        print("📧 MOCK EMAIL")
        return True

# ✅ Implementación 3 — se puede agregar SIN modificar nada
class SendGridEmailSender(IEmailSender):
    def __init__(self, api_key: str): ...
    async def send(self, recipient, subject, body, html_body=None) -> bool:
        # lógica SendGrid
        ...
```

Para usar `SendGridEmailSender`, solo se cambia `dependencies.py`:

```python
def get_email_sender() -> IEmailSender:
    provider = os.getenv("EMAIL_PROVIDER", "smtp")
    if provider == "sendgrid":
        return SendGridEmailSender(os.getenv("SENDGRID_API_KEY"))
    elif os.getenv("ENVIRONMENT") == "production":
        return SMTPEmailSender(...)
    return MockEmailSender()
```

Lo mismo aplica para `ITemplateEngine`: se puede agregar `MakoTemplateEngine` o `HandlebarsTemplateEngine` sin modificar `EmailService` ni `UserService`.

---

### 3️⃣ Liskov Substitution Principle

**"Los objetos de una subclase deben poder reemplazar a los de la clase base sin romper el comportamiento"**

`MockEmailSender` reemplaza completamente a `SMTPEmailSender`:

```python
# EmailService no sabe si usa SMTP o Mock
class EmailService:
    def __init__(self, sender: IEmailSender):  # ← acepta la interfaz
        self.sender = sender

    async def send_email(self, email_data):
        success = await self.sender.send(...)   # funciona con cualquier impl
        ...

# Ambas son intercambiables sin cambiar EmailService:
service_prod = EmailService(SMTPEmailSender(...))   # producción
service_dev  = EmailService(MockEmailSender())       # desarrollo/testing
```

---

### 4️⃣ Interface Segregation Principle

**"Los clientes no deben depender de interfaces que no usan"**

Las interfaces son específicas y pequeñas:

```python
# ❌ MAL — interfaz dios
class IEmailManager(ABC):
    def send(self): ...
    def save_to_db(self): ...
    def render_template(self): ...
    def validate_address(self): ...

# ✅ BIEN — interfaces cohesivas y pequeñas

class IEmailSender(ABC):         # 1 método
    async def send(self, ...): ...

class ITemplateEngine(ABC):      # 1 método
    def render(self, template_name, context): ...

class IEmailRepository(ABC):     # 6 métodos cohesivos
    async def create(self, ...): ...
    async def get_by_id(self, ...): ...
    async def get_all(self, ...): ...
    async def update(self, ...): ...
    async def delete(self, ...): ...
    async def count(self): ...

class IUserRepository(ABC):      # 6 métodos cohesivos
    async def create(self, ...): ...
    async def get_by_id(self, ...): ...
    # ...
```

`EmailService` recibe `IEmailSender` e `ITemplateEngine` por separado. Si solo necesita enviar emails, puede recibir solo `IEmailSender` sin `ITemplateEngine`.

---

### 5️⃣ Dependency Inversion Principle

**"Depende de abstracciones, no de concreciones"**

```python
# ❌ MAL — acoplamiento fuerte
class EmailService:
    def __init__(self):
        self.repository = EmailRepository(db)       # concreta
        self.sender     = SMTPEmailSender()          # concreta
        self.engine     = Jinja2TemplateEngine()     # concreta

# ✅ BIEN — depende de interfaces
class EmailService:
    def __init__(
        self,
        repository: IEmailRepository,     # ← interfaz
        sender: IEmailSender,             # ← interfaz
        template_engine: ITemplateEngine  # ← interfaz
    ):
        self.repository = repository
        self.sender = sender
        self.template_engine = template_engine
```

El wiring concreto ocurre únicamente en `dependencies.py`:

```python
def get_email_service(
    repository: EmailRepository = Depends(get_email_repository),
    sender: IEmailSender = Depends(get_email_sender),
    template_engine: ITemplateEngine = Depends(get_template_engine)
) -> EmailService:
    return EmailService(repository, sender, template_engine)
```

---

## 🔄 Flujo de Datos Completo

### Ejemplo: Enviar email con plantilla (usuario autenticado)

```
1. Cliente HTTP
   POST /api/users/me/send-template
   Authorization: Bearer eyJhbGci...
   { "recipient": "...", "subject": "...", "template_name": "welcome.html", "template_data": {...} }

2. user_routes.py
   @user_router.post("/me/send-template")
   async def send_with_template(
       data: SendWithTemplateRequest,
       current_user = Depends(get_current_active_user),  ← valida JWT + status
       controller   = Depends(get_user_controller)
   )

3. auth_middleware.py (get_current_active_user)
   ├─ HTTPBearer extrae el token del header Authorization
   ├─ decode_access_token(token) → payload
   ├─ UserRepository.get_by_id(payload["sub"]) → User
   └─ verifica user.status == ACTIVE → 403 si no

4. UserController.send_with_template(current_user, data)
   └─ delega a UserService.send_email_with_template(...)

5. UserService.send_email_with_template(user_id, recipient, subject, template_name, template_data)
   ├─ a) Jinja2TemplateEngine.render("welcome.html", template_data)
   │      → FileNotFoundError → HTTPException 404 si no existe
   ├─ b) EmailRepository.create(EmailCreate) → Email(status=PENDING)
   ├─ c) IEmailSender.send(recipient, subject, body, html_body)
   │      → SMTPEmailSender (prod) o MockEmailSender (dev)
   └─ d) EmailRepository.update_status(id, SENT | FAILED)

6. Respuesta al cliente
   201 Created
   { "id": 7, "recipient": "...", "status": "sent", "sent_at": "...", ... }
```

---

## 🧩 Inyección de Dependencias

FastAPI resuelve automáticamente el árbol de dependencias en cada request. `dependencies.py` es el único lugar donde se ensambla el grafo de objetos:

```python
# dependencies.py — el único "lugar de ensamblaje"

# INFRAESTRUCTURA
def get_db() -> Generator[Session]:
    db = SessionLocal()
    try: yield db
    finally: db.close()

def get_email_sender() -> IEmailSender:
    if os.getenv("ENVIRONMENT") == "production":
        port = int(os.getenv("SMTP_PORT", "587"))
        return SMTPEmailSender(use_tls=(port==587), use_ssl=(port==465))
    return MockEmailSender()

def get_template_engine() -> ITemplateEngine:
    return Jinja2TemplateEngine(templates_dir="templates")

# REPOSITORIOS
def get_email_repository(db = Depends(get_db)) -> EmailRepository:
    return EmailRepository(db)

def get_user_repository(db = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

# SERVICIOS
def get_auth_service(
    repository = Depends(get_user_repository),
    sender     = Depends(get_email_sender),
    template   = Depends(get_template_engine)
) -> AuthService:
    return AuthService(repository, sender, template)

# CONTROLADORES
def get_auth_controller(
    auth_service = Depends(get_auth_service)
) -> AuthController:
    return AuthController(auth_service)
```

FastAPI resuelve `get_auth_controller` → `get_auth_service` → `get_user_repository` → `get_db` automáticamente por cada request, con el ciclo de vida correcto (la sesión de BD se cierra al terminar).

---

## 📦 Separación de Responsabilidades por Servicio

| Servicio | Responsabilidad | NO hace |
|---|---|---|
| `AuthService` | Registro, login, cambio de contraseña, token de verificación | Gestión de perfil, bandeja de emails |
| `UserService` | Perfil, bandeja, reenvío, envío con plantilla, email_key, funciones admin | Login, hashing de contraseñas |
| `EmailService` | Pipeline CRUD de emails, envío directo, paginación global | Gestión de usuarios, autenticación |

Esta separación evita el antipatrón "god service" y facilita el mantenimiento independiente de cada área.

---

## 🧪 Testabilidad

La arquitectura facilita el testing unitario sin infraestructura real:

```python
# test_user_service.py (ejemplo)

class MockUserRepository:
    async def get_by_id(self, user_id): return User(id=1, name="Test", ...)
    async def update_status(self, user_id, status): pass

class MockEmailRepository:
    async def get_by_user_id(self, user_id, skip, limit): return []
    async def count_by_user(self, user_id): return 0

class MockSender:
    async def send(self, recipient, subject, body, html_body=None): return True

# Servicio completamente testeado sin BD ni SMTP:
service = UserService(
    user_repository=MockUserRepository(),
    email_repository=MockEmailRepository(),
    sender=MockSender(),
    template_engine=None
)

result = await service.get_my_inbox(user_id=1, page=1, page_size=10)
assert result.total == 0
```

---

## 🚀 Extensibilidad — Próximos Pasos

| Extensión | Dónde agregar | Qué no se modifica |
|---|---|---|
| Proveedor SendGrid/AWS SES | `utils/sendgrid_sender.py` + `dependencies.py` | Servicios, controladores, rutas |
| Motor de plantillas alternativo | `utils/mako_engine.py` + `dependencies.py` | Servicios, controladores, rutas |
| Cola de emails (Celery) | Nuevo servicio + `dependencies.py` | Lógica de negocio existente |
| Nuevo rol (moderador) | `models/user_models.py` + `middlewares/` | Código de usuario/admin existente |
| Rate limiting | `middlewares/` + `main.py` | Lógica de negocio |
| Logging estructurado | `core/logger.py` + reemplazar `print()` | Lógica de negocio |
| Tests | `tests/` con mocks | Código de producción |

---

*Documentado: Febrero 2026 — Email Python FastAPI v1.0.0*