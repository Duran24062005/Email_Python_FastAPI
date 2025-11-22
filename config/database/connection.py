from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from config.config import database_config
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


def init_db():
    """
    Inicializa la base de datos creando todas las tablas.
    Llamar esto al inicio de la aplicación.
    """
    from models.email_model import Base
    from sqlalchemy import text
    
    try:
        # Verificar si el tipo ENUM existe, si no, crearlo
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT 1 FROM pg_type WHERE typname = 'emailstatus'")
            )
            
            if not result.fetchone():
                conn.execute(
                    text("CREATE TYPE emailstatus AS ENUM ('pending', 'sent', 'failed')")
                )
                conn.commit()
                print("✅ Tipo ENUM 'emailstatus' creado")
        
        # Crear todas las tablas
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas verificadas/creadas")
        
    except Exception as e:
        print(f"⚠️  Base de datos ya inicializada o error: {e}")