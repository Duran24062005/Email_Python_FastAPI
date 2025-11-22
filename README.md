# 📧 Email Python FastAPI

API REST para envío de emails con plantillas personalizables en HTML, construida con FastAPI y siguiendo principios SOLID.

## 🏗️ Arquitectura

Este proyecto implementa una arquitectura limpia basada en los principios SOLID:

### Estructura del Proyecto

```
├── config/
│   ├── config.py                    # Configuración de la app
│   └── database/
│       └── connection.py            # Conexión a base de datos
├── models/
│   └── email_model.py              # Modelos de base de datos
├── schemas/
│   └── email_schema.py             # Schemas Pydantic (DTOs)
├── interfaces/
│   └── email_interfaces.py         # Interfaces (contratos)
├── repositories/
│   └── email_repository.py         # Acceso a datos
├── services/
│   └── email_service.py            # Lógica de negocio
├── controllers/
│   └── email_controller.py         # Capa de presentación
├── utils/
│   ├── smtp_email_sender.py        # Implementación de envío SMTP
│   └── template_engine.py          # Motor de plantillas Jinja2
├── templates/                       # Plantillas HTML
│   └── welcome.html
├── routes/
│   └── email_routes.py             # Definición de endpoints
├── dependencies.py                  # Inyección de dependencias
└── main.py                         # Punto de entrada
```

### Principios SOLID Implementados

#### ✅ S - Single Responsibility Principle
Cada clase tiene una única responsabilidad:
- `EmailRepository`: Solo maneja acceso a datos
- `EmailService`: Solo contiene lógica de negocio
- `EmailController`: Solo maneja peticiones HTTP
- `SMTPEmailSender`: Solo se encarga de enviar emails

#### ✅ O - Open/Closed Principle
El sistema está abierto para extensión pero cerrado para modificación:
- Puedes crear nuevos `EmailSender` sin modificar código existente
- Puedes agregar nuevos `TemplateEngine` sin afectar el resto

#### ✅ L - Liskov Substitution Principle
Las implementaciones son intercambiables:
- `SMTPEmailSender` y `MockEmailSender` implementan `IEmailSender`
- Cualquier implementación puede reemplazar a otra sin problemas

#### ✅ I - Interface Segregation Principle
Interfaces específicas y cohesivas:
- `IEmailRepository`: Operaciones de base de datos
- `IEmailSender`: Operaciones de envío
- `ITemplateEngine`: Operaciones de renderizado

#### ✅ D - Dependency Inversion Principle
Las dependencias apuntan a abstracciones:
- `EmailService` depende de `IEmailRepository`, no de `EmailRepository`
- Fácil cambiar de SMTP a SendGrid o AWS SES

## 🚀 Instalación

### 1. Clonar repositorio

```bash
git clone <tu-repositorio>
cd Email_Python_FastAPI
```

### 2. Crear entorno virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Copia `.env.example` a `.env` y configura tus credenciales:

```bash
cp .env.example .env
```

Edita `.env` con tu información:

```env
# Base de datos
PGHOST=localhost
PGPORT=5432
PGUSER=postgres
PGPASSWORD=tu_password
PGDATABASE=email_db

# SMTP (ejemplo con Gmail)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu_email@gmail.com
SMTP_PASSWORD=tu_app_password

# Entorno
ENVIRONMENT=development  # Usa 'production' para SMTP real
```

### 5. Crear base de datos

```sql
CREATE DATABASE email_db;
```

### 6. Ejecutar aplicación

```bash
uvicorn main:app --reload
```

La API estará disponible en: `http://localhost:8000`

## 📚 Uso de la API

### Documentación interactiva

Accede a la documentación Swagger en: `http://localhost:8000/docs`

### Ejemplos de uso

#### 1. Enviar email con texto plano

```bash
curl -X POST "http://localhost:8000/emails/send" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient": "usuario@example.com",
    "subject": "Prueba de email",
    "body": "Este es un email de prueba"
  }'
```

#### 2. Enviar email con HTML directo

```bash
curl -X POST "http://localhost:8000/emails/send" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient": "usuario@example.com",
    "subject": "Email con HTML",
    "html_body": "<h1>Hola</h1><p>Este es un email con HTML</p>"
  }'
```

#### 3. Enviar email con plantilla

```bash
curl -X POST "http://localhost:8000/emails/send" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient": "usuario@example.com",
    "subject": "Bienvenido",
    "template_name": "welcome.html",
    "template_data": {
      "nombre": "Juan Pérez",
      "empresa": "Mi Empresa",
      "mensaje_adicional": "Estamos felices de tenerte con nosotros"
    }
  }'
```

#### 4. Listar emails enviados

```bash
curl -X GET "http://localhost:8000/emails/?page=1&page_size=10"
```

#### 5. Obtener detalles de un email

```bash
curl -X GET "http://localhost:8000/emails/1"
```

## 🎨 Crear Plantillas HTML

Las plantillas se almacenan en la carpeta `templates/` y usan Jinja2.

### Ejemplo de plantilla

```html
<!-- templates/bienvenida.html -->
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; }
        .container { max-width: 600px; margin: 0 auto; }
        .header { background-color: #4CAF50; color: white; padding: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>¡Bienvenido {{ nombre }}!</h1>
        </div>
        <div class="content">
            <p>Hola {{ nombre }},</p>
            <p>Gracias por unirte a {{ empresa }}.</p>
            {% if mensaje_extra %}
            <p>{{ mensaje_extra }}</p>
            {% endif %}
        </div>
    </div>
</body>
</html>
```

### Variables disponibles en plantillas

Cualquier dato que pases en `template_data` estará disponible en la plantilla:

```python
{
    "template_name": "bienvenida.html",
    "template_data": {
        "nombre": "Juan",
        "empresa": "TechCorp",
        "mensaje_extra": "Tu cuenta ha sido activada"
    }
}
```

## 🔧 Extender la Funcionalidad

### Agregar un nuevo proveedor de email (ej: SendGrid)

1. Crea una nueva clase que implemente `IEmailSender`:

```python
# utils/sendgrid_sender.py
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from interfaces.email_interfaces import IEmailSender

class SendGridEmailSender(IEmailSender):
    def __init__(self, api_key: str):
        self.client = SendGridAPIClient(api_key)
    
    async def send(self, recipient, subject, body, html_body=None):
        message = Mail(
            from_email='tu@email.com',
            to_emails=recipient,
            subject=subject,
            html_content=html_body or body
        )
        try:
            self.client.send(message)
            return True
        except Exception:
            return False
```

2. Actualiza `dependencies.py`:

```python
def get_email_sender() -> IEmailSender:
    provider = os.getenv("EMAIL_PROVIDER", "smtp")
    
    if provider == "sendgrid":
        return SendGridEmailSender(os.getenv("SENDGRID_API_KEY"))
    else:
        return SMTPEmailSender()
```

¡Y listo! Sin modificar ninguna otra parte del código.

## 🧪 Testing

Para probar sin enviar emails reales, mantén `ENVIRONMENT=development` en tu `.env`. Esto usará el `MockEmailSender` que solo imprime en consola.

## 📝 Notas Importantes

- **Gmail**: Si usas Gmail, necesitas una "contraseña de aplicación", no tu contraseña normal
- **Base de datos**: Las tablas se crean automáticamente al iniciar la app
- **Plantillas**: Asegúrate de que la carpeta `templates/` existe antes de usar plantillas
- **CORS**: Configurado para aceptar todas las origenes en desarrollo

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.

---

**Desarrollado con ❤️ usando FastAPI y principios SOLID**