import os
from dotenv import load_dotenv

load_dotenv()


def _parse_cors_origins() -> list[str]:
    raw_origins = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000,https://swift-mailer.vercel.app",
    )
    return [origin.strip().rstrip("/") for origin in raw_origins.split(",") if origin.strip()]

app_config = {
    "APP_NAME": "Email_Python_FastAPI",
    "VERSION": "1.0.0",
    "DESCRIPTION": "API for sending emails using FastAPI and Python",
    "CONTACT_NAME": "Administrador",
    "PORT": os.getenv("PORT") or 8001,
    "HOST": os.getenv("HOST") or "0.0.0.0",
    "DOMAIN": os.getenv("DOMAIN") or "http://127.0.0.1:8001/",
    "CORS_ORIGINS": _parse_cors_origins(),
}

database_config = {
    "DB_HOST": os.getenv("PGHOST") or "localhost",
    "DB_PORT": os.getenv("PGPORT") or 5432,
    "DB_USER": os.getenv("PGUSER") or "postgres",
    "DB_PASSWORD": os.getenv("PGPASSWORD") or "your_password",
    "DB_NAME": os.getenv("PGDATABASE") or "your_database"
}
