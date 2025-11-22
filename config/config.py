import os
from dotenv import load_dotenv

load_dotenv()

app_config = {
    "APP_NAME": "Email_Python_FastAPI",
    "VERSION": "1.0.0",
    "DESCRIPTION": "API para enviar correos electrónicos usando FastAPI y Python",
    "CONTACT_NAME": "Administrador",
    "PORT": os.getenv("PORT") or 8000,
    "HOST": os.getenv("HOST") or "0.0.0.0"
}

database_config = {
    "DB_HOST": os.getenv("PGHOST") or "localhost",
    "DB_PORT": os.getenv("PGPORT") or 5432,
    "DB_USER": os.getenv("PGUSER") or "your_username",
    "DB_PASSWORD": os.getenv("PGDATABASE") or "your_password",
    "DB_NAME": os.getenv("PGDATABASE") or "your_database"
}