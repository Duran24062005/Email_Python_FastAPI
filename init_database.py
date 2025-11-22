"""
Script para inicializar la base de datos
Ejecutar: python init_database.py
"""

from sqlalchemy import create_engine, text
from config.config import database_config
from models.email_model import Base, EmailStatus
import sys

def create_database():
    """Crea la base de datos si no existe"""
    # Conectar a postgres para crear la base de datos
    admin_url = f"postgresql://{database_config['DB_USER']}:{database_config['DB_PASSWORD']}@{database_config['DB_HOST']}:{database_config['DB_PORT']}/postgres"
    
    try:
        engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
        
        with engine.connect() as conn:
            # Verificar si la base de datos existe
            result = conn.execute(
                text(f"SELECT 1 FROM pg_database WHERE datname = '{database_config['DB_NAME']}'")
            )
            
            if not result.fetchone():
                # Crear base de datos
                conn.execute(text(f"CREATE DATABASE {database_config['DB_NAME']}"))
                print(f"✅ Base de datos '{database_config['DB_NAME']}' creada exitosamente")
            else:
                print(f"ℹ️  Base de datos '{database_config['DB_NAME']}' ya existe")
        
        engine.dispose()
        
    except Exception as e:
        print(f"❌ Error al crear la base de datos: {e}")
        sys.exit(1)


def create_enum_type():
    """Crea el tipo ENUM si no existe"""
    db_url = f"postgresql://{database_config['DB_USER']}:{database_config['DB_PASSWORD']}@{database_config['DB_HOST']}:{database_config['DB_PORT']}/{database_config['DB_NAME']}"
    
    try:
        engine = create_engine(db_url)
        
        with engine.connect() as conn:
            # Verificar si el tipo ENUM existe
            result = conn.execute(
                text("SELECT 1 FROM pg_type WHERE typname = 'emailstatus'")
            )
            
            if not result.fetchone():
                # Crear tipo ENUM
                conn.execute(
                    text("CREATE TYPE emailstatus AS ENUM ('pending', 'sent', 'failed')")
                )
                conn.commit()
                print("✅ Tipo ENUM 'emailstatus' creado exitosamente")
            else:
                print("ℹ️  Tipo ENUM 'emailstatus' ya existe")
        
        engine.dispose()
        
    except Exception as e:
        print(f"⚠️  Advertencia al crear ENUM: {e}")


def create_tables():
    """Crea todas las tablas"""
    db_url = f"postgresql://{database_config['DB_USER']}:{database_config['DB_PASSWORD']}@{database_config['DB_HOST']}:{database_config['DB_PORT']}/{database_config['DB_NAME']}"
    
    try:
        engine = create_engine(db_url)
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas creadas exitosamente")
        engine.dispose()
        
    except Exception as e:
        print(f"❌ Error al crear tablas: {e}")
        sys.exit(1)


def main():
    """Función principal"""
    print("=" * 60)
    print("🔧 Inicializando base de datos")
    print("=" * 60)
    
    # Paso 1: Crear base de datos
    print("\n1️⃣  Creando base de datos...")
    create_database()
    
    # Paso 2: Crear tipo ENUM
    print("\n2️⃣  Creando tipo ENUM...")
    create_enum_type()
    
    # Paso 3: Crear tablas
    print("\n3️⃣  Creando tablas...")
    create_tables()
    
    print("\n" + "=" * 60)
    print("✅ Base de datos inicializada correctamente")
    print("=" * 60)
    print("\n🚀 Ahora puedes ejecutar: uvicorn main:app --reload")


if __name__ == "__main__":
    main()