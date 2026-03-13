# 📧 Email Python FastAPI

API REST para gestión y envío de emails con plantillas HTML personalizables, autenticación JWT, verificación de email y administración de usuarios. Construida con FastAPI y diseñada siguiendo los principios SOLID.

## ✨ Funcionalidades

**Para usuarios generales:**
- Registro y autenticación con JWT
- Verificación de email (token enviado al registrarse)
- Bandeja de salida paginada con todos los emails enviados
- Reenvío de emails existentes
- Envío de emails usando plantillas HTML predefinidas (Jinja2)
- Guardado de clave SMTP personal

**Para administradores:**
- Listado y búsqueda de usuarios (paginado)
- Aprobación de cuentas pendientes (con email de notificación automático)
- Cambio de estado de usuarios (active, pending, blocked, deleted)
- Actualización y eliminación de usuarios
- Estadísticas del sistema

## 🏗️ Arquitectura

Arquitectura en capas basada en los principios SOLID:

```
Routes → Middlewares → Controllers → Services → Repositories → PostgreSQL
                                              └→ IEmailSender (SMTP/Mock)
                                              └→ ITemplateEngine (Jinja2)
```

Todo el wiring de dependencias ocurre en `dependencies.py`. Los servicios dependen de interfaces, no de implementaciones concretas (Dependency Inversion). Ver [docs/architecture.md](docs/architecture.md) para el detalle completo.

### Estructura del Proyecto

```
├── app/
│   ├── config/                  # Configuración y conexión a BD
│   ├── core/                    # Seguridad (JWT, bcrypt) y excepciones de dominio
│   ├── interfaces/              # Contratos ABC
│   ├── models/                  # Modelos SQLAlchemy
│   ├── schemas/                 # DTOs Pydantic
│   ├── repositories/            # Acceso a datos
│   ├── services/                # Lógica de negocio
│   ├── controllers/             # Capa HTTP
│   ├── middlewares/             # JWT auth, roles, CORS
│   ├── routes/                  # Endpoints
│   ├── utils/                   # SMTPEmailSender, MockEmailSender, Jinja2TemplateEngine
│   ├── templates/               # Plantillas HTML
│   ├── static/                  # Landing page estática
│   ├── dependencies.py          # Inyección de dependencias
│   ├── init_database.py         # Script opcional de inicialización
│   └── main.py                  # Punto de entrada FastAPI
├── docs/                        # Documentación del proyecto
├── prds/                        # PRDs funcionales
└── Dockerfile
```

## 🚀 Instalación

### Opción A: Docker Compose (recomendado)

```bash
git clone <tu-repositorio>
cd Email_Python_FastAPI

cp .env.example .env
# Editar .env con tus credenciales

docker compose up --build
```

API disponible en `http://localhost:8001` · Swagger UI en `http://localhost:8001/`

### Opción B: Local sin Docker

```bash
# 1. Entorno virtual
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
cp .env.example .env
# Editar .env

# 4. Crear base de datos PostgreSQL
createdb email_db
# O ejecutar: python app/init_database.py

# 5. Ejecutar
cd app
uvicorn main:app --reload --port 8001
```

## ⚙️ Configuración

Copia `.env.example` a `.env` y completa las variables:

```env
# JWT
SECRET_KEY=tu-clave-secreta-muy-larga
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Entorno (development usa MockEmailSender)
ENVIRONMENT=development

# SMTP (solo necesario en production)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx   # contraseña de aplicación

# PostgreSQL
PGHOST=localhost
PGPORT=5432
PGUSER=postgres
PGPASSWORD=tu_password
PGDATABASE=email_db
```

> **Gmail:** Necesitas una "contraseña de aplicación", no tu contraseña normal. Cuenta Google → Seguridad → Verificación en 2 pasos → Contraseñas de aplicaciones.

## 📚 Uso de la API

La referencia completa está en [docs/API_REFERENCE.md](docs/API_REFERENCE.md). Aquí algunos ejemplos rápidos:

### Registro y login

```bash
# Registrar usuario
curl -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "Juan Pérez", "email": "juan@example.com", "password": "mipassword123"}'

# Login → obtener JWT
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "juan@example.com", "password": "mipassword123"}'
```

### Enviar email con plantilla

```bash
curl -X POST http://localhost:8001/emails/send \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 3,
    "recipient": "alexisdurangomez588@gmail.com",
    "subject": "Bienvenido",
    "template_name": "welcome.html",
    "template_data": {
      "nombre": "Juan",
      "empresa": "Mi Empresa"
    }
  }'
```

### Enviar email con formulario y adjunto

```bash
curl -X POST http://localhost:8001/emails/send/form \
  -F "user_id=3" \
  -F "recipient=alexisdurangomez588@gmail.com" \
  -F "subject=Bienvenido" \
  -F "template_name=welcome.html" \
  -F 'template_data={"nombre":"Juan","empresa":"Mi Empresa"}' \
  -F "pdf_attachment=@./archivo.pdf"
```

### Enviar email autenticado con plantilla

```bash
curl -X POST http://localhost:8001/api/users/me/send-template \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient": "cliente@example.com",
    "subject": "Bienvenido",
    "template_name": "welcome.html",
    "template_data": {
      "nombre": "Carlos",
      "empresa": "Mi Empresa",
      "mensaje_adicional": "Gracias por unirte"
    }
  }'
```

### Ver bandeja de salida

```bash
curl http://localhost:8001/api/users/me/inbox?page=1&page_size=10 \
  -H "Authorization: Bearer <token>"
```

## 🎨 Plantillas HTML

Las plantillas están en `app/templates/` y usan Jinja2. Las disponibles son:

| Plantilla | Variables requeridas |
|---|---|
| `welcome.html` | `nombre`, `empresa` |
| `welcome_educonnect.html` | `nombre`, `empresa` |
| `account_approved.html` | `nombre`, `empresa`, `role`, `login_link` |
| `my_website.html` | `nombre` |

Para agregar una plantilla nueva, crea el archivo `.html` en `app/templates/` y úsalo por nombre en el endpoint de envío.

## 🔧 Extender la Funcionalidad

### Agregar un proveedor de email (ej: SendGrid)

1. Crea `app/utils/sendgrid_sender.py` implementando `IEmailSender`:

```python
from interfaces.email_interfaces import IEmailSender

class SendGridEmailSender(IEmailSender):
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def send(self, recipient, subject, body, html_body=None) -> bool:
        # lógica de SendGrid
        return True
```

2. Actualiza `app/dependencies.py`:

```python
def get_email_sender() -> IEmailSender:
    provider = os.getenv("EMAIL_PROVIDER", "smtp")
    if provider == "sendgrid":
        return SendGridEmailSender(os.getenv("SENDGRID_API_KEY"))
    elif os.getenv("ENVIRONMENT") == "production":
        return SMTPEmailSender(...)
    return MockEmailSender()
```

Sin modificar ninguna otra parte del código.

## 🧪 Modo desarrollo

Con `ENVIRONMENT=development`, la app usa `MockEmailSender`: los emails se imprimen en consola y no se envían realmente. Esto permite desarrollar sin credenciales SMTP.

```
============================================================
📧 MOCK EMAIL
Para: usuario@example.com
Asunto: Bienvenido
Cuerpo: Por favor visualiza este email en un cliente...
HTML: <html>...</html>
============================================================
```

## 📖 Documentación

| Documento | Descripción |
|---|---|
| [SYSTEM_ARTIFACT.md](docs/SYSTEM_ARTIFACT.md) | Documento maestro del sistema: arquitectura, modelos, flujos, decisiones de diseño |
| [API_REFERENCE.md](docs/API_REFERENCE.md) | Referencia completa de todos los endpoints |
| [architecture.md](docs/architecture.md) | Guía detallada de la arquitectura SOLID con ejemplos de código |
| [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Guía de resolución de problemas comunes |
| [STYLE_DOCSTRINGS_GUIDE.md](docs/STYLE_DOSCTRINGS_GUIDE.md) | Estándar de docstrings para Swagger UI |
| [gitflow.md](docs/gitflow.md) | Guía completa de GitFlow para el equipo |

La documentación interactiva (Swagger UI) está disponible en `http://localhost:8001/` cuando la app está corriendo.

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama: `git checkout -b feature/nueva-funcionalidad`
3. Commit siguiendo Conventional Commits: `git commit -m "feat: descripción"`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Abre un Pull Request hacia `develop`

Ver [docs/gitflow.md](docs/gitflow.md) para el flujo de trabajo completo del equipo.

## 📄 Licencia

MIT

---

**Desarrollado con FastAPI y principios SOLID**
