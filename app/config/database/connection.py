from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from app.config.config import database_config
from typing import Generator

# Construir URL de conexión
DATABASE_URL = f"postgresql://{database_config['DB_USER']}:{database_config['DB_PASSWORD']}@{database_config['DB_HOST']}:{database_config['DB_PORT']}/{database_config['DB_NAME']}"

# Crear engine de SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verifica conexiones antes de usarlas
    echo=False,  # Cambia a True para debug SQL
)

# Crear SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency para obtener sesión de base de datos.
    Se usa en FastAPI con Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> bool:
    """
    Verifica que la base de datos responda sin mutar el esquema.
    Las migraciones deben ejecutarse exclusivamente con Alembic.
    """
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return True
