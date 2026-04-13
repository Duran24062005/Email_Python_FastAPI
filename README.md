# Email Python FastAPI

API REST para gestión y envío de emails con plantillas HTML, autenticación JWT, verificación de cuentas y administración de usuarios. Está construida con FastAPI, PostgreSQL y una arquitectura en capas basada en principios SOLID.

## Funcionalidades

- Registro y autenticación con JWT
- Verificación de email con token
- Bandeja de salida paginada
- Reenvío de emails enviados
- Envío con texto plano, HTML o plantillas Jinja2
- Guardado de clave SMTP personal
- Gestión administrativa de usuarios y estados

## Estructura

```text
app/
docs/
prds/
Dockerfile
docker-compose.yml
requirements.txt
```

## Inicio rápido con Docker

```bash
cp .env.example .env
docker compose up -d postgres
docker compose run --rm email-api alembic upgrade head
docker compose up --build email-api
```

Queda disponible en:

- API: `http://localhost:8001`
- Swagger: `http://localhost:8001/docs`
- Healthcheck: `http://localhost:8001/health`

La guía Docker detallada está en [docs/docker.md](docs/docker.md).

## Ejecución local sin Docker

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --port 8001
```

Si ejecutas la base de datos fuera de Docker, ajusta `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD` y `PGDATABASE` en tu `.env`.

## Migraciones con Alembic

El esquema ya no se crea automaticamente al iniciar la API. Debes aplicar migraciones antes de levantar el servidor:

```bash
alembic upgrade head
```

Comandos utiles:

```bash
alembic current
alembic history
alembic downgrade -1
```

`database.sql` se mantiene como bootstrap completo para entornos nuevos, pero Alembic es la fuente de verdad para la evolucion incremental del esquema.

## Variables de entorno

Ejemplo mínimo:

```env
PORT=8001
HOST=0.0.0.0
DOMAIN=http://localhost:8001/
ENVIRONMENT=development

SECRET_KEY=change-this-secret-key-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

PGHOST=localhost
PGPORT=5432
PGUSER=admin
PGPASSWORD=admin123
PGDATABASE=email_db

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
```

Notas:

- `ENVIRONMENT=development` usa `MockEmailSender`
- `ENVIRONMENT=production` usa SMTP real
- En Docker Compose, `PGHOST` se sustituye por `postgres`

## Endpoints rápidos

```bash
curl -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Juan","email":"juan@example.com","password":"mipassword123"}'
```

```bash
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"juan@example.com","password":"mipassword123"}'
```

```bash
curl http://localhost:8001/api/users/me \
  -H "Authorization: Bearer <token>"
```

## Plantillas HTML

Las plantillas viven en `app/templates/` y se resuelven por nombre desde los endpoints de envío. Algunas plantillas existentes:

- `welcome.html`
- `account_approved.html`
- `welcome_active_count_educonnect.html`
- `welcome_inactive_count_educonnect.html`

## Documentación

- [docs/docker.md](docs/docker.md): guía de Docker y Compose
- [docs/API_REFERENCE.md](docs/API_REFERENCE.md): referencia de endpoints
- [docs/architecture.md](docs/architecture.md): arquitectura en capas
- [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md): problemas comunes
- [docs/System_Artifact.md](docs/System_Artifact.md): artefacto general del sistema
- [docs/alembic.md](docs/alembic.md): que es Alembic, como usarlo y flujo en este proyecto
- [docs/gitflow.md](docs/gitflow.md): flujo de trabajo Git

## Desarrollo

Durante desarrollo, la app expone autorecarga cuando se ejecuta con `docker compose` o `uvicorn --reload`. Para correos reales con Gmail, usa contraseña de aplicación y no la contraseña normal de la cuenta.
