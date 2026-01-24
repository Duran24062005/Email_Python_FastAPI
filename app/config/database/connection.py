"""Database connection configuration for async SQLAlchemy."""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.config.config import get_database_url

# Obtener URL de base de datos
DATABASE_URL = get_database_url()

# Crear engine asíncrono de SQLAlchemy
engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verifica conexiones antes de usarlas
    echo=False,  # Cambia a True para debug SQL
)

# Crear AsyncSessionLocal
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency para obtener sesión de base de datos asíncrona.
    Se usa en FastAPI con Depends(get_db)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """
    Inicializa la base de datos creando todas las tablas.
    Llamar esto al inicio de la aplicación.
    """
    from app.models.base import Base
    from sqlalchemy import text
    
    try:
        # Verificar si el tipo ENUM existe, si no, crearlo
        async with engine.begin() as conn:
            result = await conn.execute(
                text("SELECT 1 FROM pg_type WHERE typname = 'emailstatus'")
            )
            
            if not result.fetchone():
                await conn.execute(
                    text("CREATE TYPE emailstatus AS ENUM ('pending', 'sent', 'failed')")
                )
                await conn.commit()
                print("✅ Tipo ENUM 'emailstatus' creado")
        
        # Crear todas las tablas
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Tablas verificadas/creadas")
        
    except Exception as e:
        print(f"⚠️  Base de datos ya inicializada o error: {e}")
