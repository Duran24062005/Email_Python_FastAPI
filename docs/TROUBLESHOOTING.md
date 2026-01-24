# 🔧 Guía de Solución de Problemas

## Error: "duplicate key value violates unique constraint 'pg_type_typname_nsp_index'"

### 🔍 Causa
El tipo ENUM `emailstatus` ya existe en la base de datos de una ejecución anterior.

### ✅ Soluciones (3 opciones)

---

#### **Opción 1: Usar el script Python de inicialización** (RECOMENDADO)

```bash
# Este script maneja automáticamente el ENUM existente
python init_database.py
```

Luego ejecuta tu aplicación normalmente:
```bash
uvicorn main:app --reload
```

---

#### **Opción 2: Resetear completamente la base de datos**

Si no te importa perder los datos existentes:

```bash
# Ejecutar el script de reset
psql -U postgres -f database_reset.sql
```

Luego ejecuta:
```bash
uvicorn main:app --reload
```

---

#### **Opción 3: Eliminar el ENUM manualmente**

Si quieres mantener algunos datos:

```sql
-- Conectarse a la base de datos
psql -U postgres -d email_db

-- Eliminar la tabla (esto eliminará los datos)
DROP TABLE IF EXISTS emails CASCADE;

-- Eliminar el tipo ENUM
DROP TYPE IF EXISTS emailstatus CASCADE;

-- Salir
\q
```

Luego ejecuta la aplicación:
```bash
uvicorn main:app --reload
```

---

## Error: "psycopg2 not found"

### ✅ Solución

```bash
pip install psycopg2-binary
```

---

## Error: "connection refused" al conectar a PostgreSQL

### 🔍 Posibles causas

1. **PostgreSQL no está corriendo**
   ```bash
   # Linux
   sudo systemctl start postgresql
   sudo systemctl status postgresql
   
   # macOS
   brew services start postgresql
   
   # Windows
   # Iniciar desde Services o pgAdmin
   ```

2. **Credenciales incorrectas en .env**
   ```env
   PGHOST=localhost
   PGPORT=5432
   PGUSER=postgres
   PGPASSWORD=tu_password_correcto
   PGDATABASE=email_db
   ```

3. **PostgreSQL escucha en otro puerto**
   ```bash
   # Verificar el puerto
   psql -U postgres -c "SHOW port;"
   ```

---

## Error: "database 'email_db' does not exist"

### ✅ Solución

```bash
# Opción 1: Usar el script Python
python init_database.py

# Opción 2: Crear manualmente
psql -U postgres -c "CREATE DATABASE email_db;"
```

---

## Error al enviar emails: "authentication failed"

### 🔍 Si usas Gmail

Gmail requiere una "Contraseña de Aplicación", NO tu contraseña normal.

#### Pasos para obtener contraseña de aplicación:

1. Ve a tu cuenta de Google: https://myaccount.google.com/
2. Seguridad → Verificación en dos pasos (debes activarla)
3. Seguridad → Contraseñas de aplicaciones
4. Genera una contraseña para "Correo"
5. Usa esa contraseña en tu `.env`:

```env
SMTP_USER=tu_email@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx  # Contraseña de aplicación
```

---

## Modo desarrollo: Los emails no se envían realmente

### ✅ Esto es NORMAL

En modo desarrollo (`ENVIRONMENT=development`), la app usa `MockEmailSender` que solo imprime en consola.

Para enviar emails reales:

```env
# En tu .env
ENVIRONMENT=production
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu_email@gmail.com
SMTP_PASSWORD=tu_password_de_aplicacion
```

---

## Error: "Jinja2 TemplateNotFound"

### 🔍 Causa
La carpeta `templates/` no existe o la plantilla no está ahí.

### ✅ Solución

```bash
# Crear carpeta templates
mkdir templates

# Crear una plantilla de ejemplo
cat > templates/welcome.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Bienvenido</title>
</head>
<body>
    <h1>Hola {{ nombre }}</h1>
    <p>Bienvenido a {{ empresa }}</p>
</body>
</html>
EOF
```

---

## Error: "No module named 'interfaces'"

### 🔍 Causa
Falta crear la carpeta y el archivo de interfaces.

### ✅ Solución

```bash
# Crear carpeta
mkdir interfaces

# Crear archivo vacío __init__.py
touch interfaces/__init__.py

# El archivo email_interfaces.py debe estar ahí
```

---

## Verificar que todo está bien configurado

### Script de verificación:

```bash
# Crear archivo test_connection.py
cat > test_connection.py << 'EOF'
from config.database.connection import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        print("✅ Conexión exitosa!")
        print(f"PostgreSQL: {result.fetchone()[0]}")
except Exception as e:
    print(f"❌ Error de conexión: {e}")
EOF

# Ejecutar
python test_connection.py
```

---

## Comandos útiles de PostgreSQL

```bash
# Listar bases de datos
psql -U postgres -c "\l"

# Conectarse a email_db
psql -U postgres -d email_db

# Ver tablas
\dt

# Ver tipos ENUM
\dT

# Ver estructura de tabla
\d emails

# Ver datos
SELECT * FROM emails;

# Salir
\q
```

---

## Logs y debugging

### Ver logs detallados de SQL:

En `config/database/connection.py`:

```python
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=True,  # ← Cambia a True para ver SQL
)
```

### Ver logs de FastAPI:

```bash
# Con más detalle
uvicorn main:app --reload --log-level debug
```

---

## Limpiar todo y empezar de cero

```bash
# 1. Eliminar base de datos
psql -U postgres -c "DROP DATABASE IF EXISTS email_db;"

# 2. Eliminar archivos Python compilados
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# 3. Reiniciar
python init_database.py

# 4. Ejecutar
uvicorn main:app --reload
```

---

## ¿Sigue sin funcionar?

1. **Verifica las versiones**:
   ```bash
   python --version  # Debe ser 3.10+
   psql --version    # Debe ser PostgreSQL 12+
   ```

2. **Reinstala dependencias**:
   ```bash
   pip install --upgrade --force-reinstall -r requirements.txt
   ```

3. **Verifica el .env**:
   ```bash
   cat .env | grep -v "^#"
   ```

4. **Revisa los logs completos**:
   ```bash
   uvicorn main:app --reload 2>&1 | tee app.log
   ```

---

**Si ninguna solución funciona, revisa el archivo `app.log` generado y busca el error específico.** 📋