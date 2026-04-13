"""
Script para inicializar la base de datos.
Ejecutar desde la raiz del proyecto con: python app/init_database.py
"""

from pathlib import Path
import subprocess
import sys

from sqlalchemy import create_engine, text
from app.config.config import database_config


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


def run_alembic_upgrade():
    """Ejecuta las migraciones de Alembic sobre la base configurada."""
    project_root = Path(__file__).resolve().parents[1]

    try:
        subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            cwd=project_root,
            check=True,
        )
        print("✅ Migraciones Alembic aplicadas correctamente")
    except Exception as e:
        print(f"❌ Error al ejecutar Alembic: {e}")
        sys.exit(1)


def main():
    """Función principal"""
    print("=" * 60)
    print("🔧 Inicializando base de datos")
    print("=" * 60)
    
    # Paso 1: Crear base de datos
    print("\n1️⃣  Creando base de datos...")
    create_database()
    
    # Paso 2: Aplicar migraciones
    print("\n2️⃣  Ejecutando migraciones Alembic...")
    run_alembic_upgrade()
    
    print("\n" + "=" * 60)
    print("✅ Base de datos inicializada correctamente")
    print("=" * 60)
    print("\n🚀 Ahora puedes ejecutar: uvicorn app.main:app --reload --port 8001")


if __name__ == "__main__":
    main()
