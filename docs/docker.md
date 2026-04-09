# Docker

Esta guía deja el proyecto listo para ejecutarse con Docker de forma consistente entre desarrollo y despliegue simple.

## Archivos involucrados

- `Dockerfile`: imagen base optimizada para FastAPI
- `docker-compose.yml`: API + PostgreSQL para desarrollo local
- `.dockerignore`: reduce el contexto de build
- `.env.example`: variables base para arrancar rápido

## Inicio rápido

```bash
cp .env.example .env
docker compose up --build
```

Servicios disponibles:

- API: `http://localhost:8001`
- Swagger: `http://localhost:8001/docs`
- Healthcheck: `http://localhost:8001/health`
- PostgreSQL: `localhost:5432`

## Qué hace la configuración actual

- La imagen corre con `python:3.12-slim`
- Se instala `libpq-dev` para `psycopg2-binary`
- El contenedor principal usa un usuario no root
- La imagen base arranca en modo estable sin `--reload`
- `docker compose` activa `--reload` para desarrollo local
- PostgreSQL se inicializa con `database.sql`

## Variables importantes

Usa `.env` para personalizar:

```env
ENVIRONMENT=development
SECRET_KEY=change-this-secret-key-in-production
PGUSER=admin
PGPASSWORD=admin123
PGDATABASE=email_db
SMTP_USER=
SMTP_PASSWORD=
```

Notas:

- En `development` la app usa `MockEmailSender`
- Para envío real, cambia a `ENVIRONMENT=production` y completa SMTP
- Dentro de Docker Compose, `PGHOST` se fuerza a `postgres`

## Comandos útiles

```bash
docker compose up --build
docker compose up -d
docker compose logs -f email-api
docker compose exec email-api bash
docker compose down
docker compose down -v
```

## Producción simple

Si quieres usar solo la imagen:

```bash
docker build -t email-python-fastapi .
docker run --rm -p 8001:8001 --env-file .env email-python-fastapi
```

En ese caso recuerda apuntar `PGHOST` a una base PostgreSQL accesible desde el contenedor.

## Troubleshooting rápido

- Si la API no levanta, revisa `docker compose logs -f email-api`
- Si PostgreSQL falla, elimina volúmenes con `docker compose down -v` y vuelve a crear
- Si no salen correos reales, confirma `ENVIRONMENT=production` y credenciales SMTP
