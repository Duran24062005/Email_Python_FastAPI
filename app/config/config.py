import os
from dotenv import load_dotenv

load_dotenv()

app_config = {
    "APP_NAME": "Email_Python_FastAPI",
    "VERSION": "1.0.0",
    "DESCRIPTION": "API for sending emails using FastAPI and Python",
    "CONTACT_NAME": "Administrador",
    "PORT": os.getenv("PORT") or 8000,
    "HOST": os.getenv("HOST") or "0.0.0.0"
}

database_config = {
    "DB_HOST": os.getenv("PGHOST") or "localhost",
    "DB_PORT": os.getenv("PGPORT") or 5432,
    "DB_USER": os.getenv("PGUSER") or "your_username",
    "DB_PASSWORD": os.getenv("PGPASSWORD") or "your_password",
    "DB_NAME": os.getenv("PGDATABASE") or "your_database"
}

security_config = {
    "SECRET_KEY": os.getenv("SECRET_KEY") or "your-secret-key-change-in-production",
    "ACCESS_TOKEN_EXPIRE_MINUTES": int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
    "REFRESH_TOKEN_EXPIRE_DAYS": int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")),
    "ALGORITHM": os.getenv("ALGORITHM") or "HS256"
}

cors_config = {
    "CORS_ORIGINS": os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8080").split(",")
}


def get_database_url() -> str:
    """
    Construye la URL de conexión a la base de datos PostgreSQL usando asyncpg.
    
    Returns:
        URL de conexión en formato: postgresql+asyncpg://user:password@host:port/database
    """
    return (
        f"postgresql+asyncpg://{database_config['DB_USER']}:"
        f"{database_config['DB_PASSWORD']}@{database_config['DB_HOST']}:"
        f"{database_config['DB_PORT']}/{database_config['DB_NAME']}"
    )