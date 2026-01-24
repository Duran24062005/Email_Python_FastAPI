# 🏗️ Guía de Arquitectura - Email Python FastAPI

## 📊 Diagrama de Flujo

```
┌─────────────┐
│   Cliente   │
│  (Browser)  │
└──────┬──────┘
       │
       │ HTTP Request
       ▼
┌─────────────────────────────────────────┐
│           FastAPI Routes                │
│       (email_routes.py)                 │
│  - Define endpoints                     │
│  - Validación básica de parámetros      │
└──────────────┬──────────────────────────┘
               │
               │ Inyección de dependencias
               ▼
┌─────────────────────────────────────────┐
│         Email Controller                │
│    (email_controller.py)                │
│  - Maneja peticiones HTTP               │
│  - Valida datos de entrada              │
│  - Maneja errores HTTP                  │
│  - Retorna respuestas HTTP              │
└──────────────┬──────────────────────────┘
               │
               │ Llama métodos de negocio
               ▼
┌─────────────────────────────────────────┐
│          Email Service                  │
│       (email_service.py)                │
│  - Lógica de negocio                    │
│  - Orquesta operaciones                 │
│  - Prepara contenido de emails          │
└──────┬────────────┬─────────────────────┘
       │            │
       │            │ Renderiza plantilla
       │            ▼
       │   ┌──────────────────┐
       │   │ Template Engine  │
       │   │ (Jinja2)         │
       │   └──────────────────┘
       │
       │ Guarda/Lee datos
       ▼
┌─────────────────────┐      ┌──────────────────┐
│  Email Repository   │      │  Email Sender    │
│  (SQL Database)     │      │  (SMTP)          │
└─────────────────────┘      └──────────────────┘
```

## 🎯 Principios SOLID en Detalle

### 1️⃣ Single Responsibility Principle (SRP)

**"Una clase debe tener una sola razón para cambiar"**

#### ✅ Implementación en el proyecto:

```python
# ❌ MAL - Una clase hace demasiado
class EmailManager:
    def send_email(self, data):
        # Validar datos
        # Conectar a BD
        # Renderizar plantilla
        # Enviar email SMTP
        # Guardar registro
        pass

# ✅ BIEN - Responsabilidades separadas
class EmailController:
    # Solo maneja HTTP
    def send_email(self, data): ...

class EmailService:
    # Solo lógica de negocio
    def send_email(self, data): ...

class EmailRepository:
    # Solo acceso a datos
    def create(self, email): ...

class SMTPEmailSender:
    # Solo envío de emails
    def send(self, recipient, subject, body): ...
```

**Beneficio**: Si cambias la forma de enviar emails, solo modificas `SMTPEmailSender`.

---

### 2️⃣ Open/Closed Principle (OCP)

**"Abierto para extensión, cerrado para modificación"**

#### ✅ Implementación en el proyecto:

```python
# Interfaz base
class IEmailSender(ABC):
    @abstractmethod
    async def send(self, recipient, subject, body, html_body=None): pass

# Implementación 1: SMTP
class SMTPEmailSender(IEmailSender):
    async def send(self, recipient, subject, body, html_body=None):
        # Lógica SMTP
        pass

# Implementación 2: SendGrid (EXTENSIÓN, no modificación)
class SendGridEmailSender(IEmailSender):
    async def send(self, recipient, subject, body, html_body=None):
        # Lógica SendGrid
        pass

# Implementación 3: AWS SES (otra extensión)
class AWSEmailSender(IEmailSender):
    async def send(self, recipient, subject, body, html_body=None):
        # Lógica AWS SES
        pass
```

**Beneficio**: Puedes agregar nuevos proveedores de email sin tocar código existente.

---

### 3️⃣ Liskov Substitution Principle (LSP)

**"Los objetos de una clase derivada deben poder reemplazar a los de la clase base sin afectar la funcionalidad"**

#### ✅ Implementación en el proyecto:

```python
# El servicio NO sabe qué implementación usa
class EmailService:
    def __init__(self, sender: IEmailSender):  # ← Acepta la interfaz
        self.sender = sender
    
    async def send_email(self, email_data):
        # Funciona con CUALQUIER implementación de IEmailSender
        await self.sender.send(...)

# Todas estas son intercambiables:
service1 = EmailService(SMTPEmailSender())      # Producción
service2 = EmailService(MockEmailSender())      # Testing
service3 = EmailService(SendGridEmailSender())  # Alternativa
```

**Beneficio**: Puedes intercambiar implementaciones sin romper nada.

---

### 4️⃣ Interface Segregation Principle (ISP)

**"Los clientes no deben depender de interfaces que no usan"**

#### ✅ Implementación en el proyecto:

```python
# ❌ MAL - Interfaz muy grande
class IEmailManager(ABC):
    @abstractmethod
    def send(self): pass
    
    @abstractmethod
    def save_to_db(self): pass
    
    @abstractmethod
    def render_template(self): pass
    
    @abstractmethod
    def validate_email(self): pass

# ✅ BIEN - Interfaces específicas
class IEmailSender(ABC):
    @abstractmethod
    def send(self): pass

class IEmailRepository(ABC):
    @abstractmethod
    def create(self): pass
    @abstractmethod
    def get_by_id(self): pass

class ITemplateEngine(ABC):
    @abstractmethod
    def render(self): pass
```

**Beneficio**: Cada componente implementa solo lo que necesita.

---

### 5️⃣ Dependency Inversion Principle (DIP)

**"Depende de abstracciones, no de concreciones"**

#### ✅ Implementación en el proyecto:

```python
# ❌ MAL - Dependencia directa de implementación
class EmailService:
    def __init__(self):
        self.repository = EmailRepository()  # ← Acoplamiento fuerte
        self.sender = SMTPEmailSender()      # ← Acoplamiento fuerte

# ✅ BIEN - Dependencia de abstracción
class EmailService:
    def __init__(
        self,
        repository: IEmailRepository,  # ← Interfaz
        sender: IEmailSender           # ← Interfaz
    ):
        self.repository = repository
        self.sender = sender
```

**Beneficio**: Fácil de testear y cambiar implementaciones.

---

## 🔄 Flujo de Datos Completo

### Ejemplo: Enviar email con plantilla

```python
# 1️⃣ Cliente hace petición HTTP
POST /emails/send
{
    "recipient": "juan@example.com",
    "subject": "Bienvenido",
    "template_name": "welcome.html",
    "template_data": {"nombre": "Juan", "empresa": "TechCorp"}
}

# 2️⃣ FastAPI Route recibe la petición
@email_router.post("/send")
async def send_email(
    email: EmailCreate,
    controller: EmailController = Depends(get_email_controller)
):
    return await controller.send_email(email)

# 3️⃣ Controller valida y delega
class EmailController:
    async def send_email(self, email_data: EmailCreate):
        # Validación HTTP
        result = await self.email_service.send_email(email_data)
        # Manejo de errores HTTP
        return result

# 4️⃣ Service ejecuta lógica de negocio
class EmailService:
    async def send_email(self, email_data):
        # a) Renderizar plantilla
        html = self.template_engine.render(
            "welcome.html",
            {"nombre": "Juan", "empresa": "TechCorp"}
        )
        
        # b) Guardar en BD
        email_record = await self.repository.create(email_data)
        
        # c) Enviar email
        success = await self.sender.send(
            recipient="juan@example.com",
            subject="Bienvenido",
            body="...",
            html_body=html
        )
        
        # d) Actualizar estado
        if success:
            await self.repository.update_status(email_record.id, "sent")
        
        return email_record

# 5️⃣ Repository guarda en base de datos
class EmailRepository:
    async def create(self, email_data):
        email = Email(**email_data.dict())
        self.db.add(email)
        self.db.commit()
        return email

# 6️⃣ EmailSender envía el email
class SMTPEmailSender:
    async def send(self, recipient, subject, body, html_body):
        # Conectar SMTP y enviar
        return True

# 7️⃣ Respuesta al cliente
{
    "id": 1,
    "recipient": "juan@example.com",
    "subject": "Bienvenido",
    "status": "sent",
    "sent_at": "2024-01-15T10:30:00"
}
```

---

## 🧩 Inyección de Dependencias

### ¿Cómo funciona?

```python
# dependencies.py - Define cómo crear las instancias

def get_email_sender() -> IEmailSender:
    """Factory que decide qué implementación usar"""
    if os.getenv("ENVIRONMENT") == "production":
        return SMTPEmailSender()
    else:
        return MockEmailSender()

def get_email_repository(db: Session = Depends(get_db)):
    """Crea el repositorio con la sesión de BD"""
    return EmailRepository(db)

def get_email_service(
    repository: EmailRepository = Depends(get_email_repository),
    sender: IEmailSender = Depends(get_email_sender),
    template_engine: ITemplateEngine = Depends(get_template_engine)
):
    """Ensambla el servicio con todas sus dependencias"""
    return EmailService(repository, sender, template_engine)

def get_email_controller(
    email_service: EmailService = Depends(get_email_service)
):
    """Crea el controlador con el servicio"""
    return EmailController(email_service)
```

### En los endpoints:

```python
@email_router.post("/send")
async def send_email(
    email: EmailCreate,
    controller: EmailController = Depends(get_email_controller)
    # ↑ FastAPI inyecta automáticamente todas las dependencias
):
    return await controller.send_email(email)
```

**Beneficio**: 
- No necesitas instanciar manualmente nada
- Fácil cambiar implementaciones en un solo lugar
- Excelente para testing

---

## 🧪 Testing Facilitado

Gracias a SOLID, el testing es muy fácil:

```python
# test_email_service.py

class MockRepository(IEmailRepository):
    async def create(self, email_data):
        return Email(id=1, **email_data.dict())

class MockSender(IEmailSender):
    async def send(self, recipient, subject, body, html_body):
        return True

# Test
def test_send_email():
    # Usar mocks en lugar de implementaciones reales
    service = EmailService(
        repository=MockRepository(),
        sender=MockSender(),
        template_engine=None
    )
    
    result = await service.send_email(email_data)
    assert result.status == "sent"
```

---

## 📚 Ventajas de esta Arquitectura

| Aspecto | Beneficio |
|---------|-----------|
| **Mantenibilidad** | Cada componente tiene responsabilidad clara |
| **Escalabilidad** | Fácil agregar nuevas funcionalidades |
| **Testabilidad** | Cada capa se prueba independientemente |
| **Flexibilidad** | Cambiar implementaciones sin afectar el resto |
| **Legibilidad** | Código organizado y autodocumentado |

---

## 🚀 Próximos Pasos Sugeridos

1. **Agregar cache**: Cachear plantillas renderizadas frecuentes
2. **Agregar colas**: Usar Celery/RQ para envíos asíncronos masivos
3. **Agregar logs**: Sistema de logging estructurado
4. **Agregar métricas**: Rastrear tasa de éxito de envíos
5. **Agregar autenticación**: JWT para proteger endpoints
6. **Agregar rate limiting**: Prevenir abuso del servicio

---

**¿Preguntas?** Revisa el código, todo está documentado con comentarios explicativos. 🎓