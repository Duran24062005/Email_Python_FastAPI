# Testing

> Guía de la suite de tests unitarios: cómo ejecutarla, qué cubre y cómo se estructura.
> Los tests corren en CI en cada push/PR a `main` (ver [build_and_test.yaml](../.github/workflows/build_and_test.yaml)).

## Ejecutar los tests

```bash
# 1. Instalar dependencias de desarrollo (incluye pytest y pytest-asyncio)
pip install -r requirements-dev.txt

# 2. Ejecutar toda la suite
pytest

# 3. Ejecutar solo un archivo o un test
pytest tests/test_auth_service.py
pytest tests/test_auth_service.py::test_login_success_returns_token_and_updates_last_login
```

Los tests no requieren PostgreSQL ni SMTP: los repositorios se prueban contra
SQLite en memoria y el resto usa fakes. Solo necesitas Python 3.12+ (el código
del proyecto usa f-strings anidadas, sintaxis PEP 701, que no existe en 3.10/3.11).

## Estructura

```text
tests/
├── conftest.py            # Fakes compartidos + fixture de SQLite en memoria
├── test_core_security.py  # bcrypt y JWT (hash, verify, create/decode token)
├── test_schemas.py        # Validación de schemas Pydantic
├── test_template_engine.py# Jinja2TemplateEngine y SimpleTemplateEngine
├── test_repositories.py   # UserRepository y EmailRepository (SQLite real)
├── test_email_service.py  # EmailService (envío, adjuntos, estados, fallos)
├── test_auth_service.py   # AuthService (registro, login, cambio de contraseña)
├── test_user_service.py   # UserService (perfil, inbox, reenvío, admin)
├── test_middlewares.py    # get_current_user, get_current_active_user, require_admin
└── test_app_smoke.py      # Smoke test: /health, / y /docs
pytest.ini                 # Configuración: testpaths y asyncio_mode=auto
```

## Estrategia

### Fakes en memoria para servicios (`tests/conftest.py`)

Los servicios (`AuthService`, `UserService`, `EmailService`) reciben sus
dependencias por constructor (Inversión de Dependencias), lo que permite
inyectar fakes:

- `FakeUserRepository` / `FakeEmailRepository`: repositorios con la misma
  interfaz que los reales, respaldados por diccionarios en memoria.
- `FakeSender`: registra cada envío (`sent`) y permite configurar si el envío
  tiene éxito o lanza una excepción.
- `FakeTemplateEngine`: renderiza a un HTML determinista y puede simular que
  una plantilla no existe (`missing`).

### SQLite en memoria para repositorios (`tests/test_repositories.py`)

Los repositorios reales se prueban contra `sqlite:///:memory:` con
`StaticPool`. SQLite implementa la misma API de sesión de SQLAlchemy que
PostgreSQL, así que la lógica de acceso a datos (CRUD, filtros, paginación,
orden) se cubre sin levantar una base externa.

### Smoke test de la aplicación (`tests/test_app_smoke.py`)

Verifica que la app importa y que `/health`, `/` (redirección a `/docs`) y
`/docs` responden, sin necesidad de base de datos.

## Qué se cubre

| Módulo | Casos principales |
|---|---|
| `core/security` | hash/verify bcrypt (incl. límite de 72 bytes), generación y decodificación de JWT, tokens expirados o con firma inválida |
| `schemas` | reglas de validación: contraseñas cortas o >72 bytes, emails inválidos, campos opcionales con `exclude_unset` |
| `utils/template_engine` | render de variables, autoescape XSS, plantilla inexistente, listado de plantillas |
| `repositories` | CRUD de usuarios y emails, estados, `get_pending_users`, bandeja por usuario con orden desc, conteos, borrado lógico vs. físico |
| `services/email` | envío plano/HTML/plantilla, adjuntos, estados SENT/FAILED ante `False` o excepción, fallback si falta plantilla, CRUD |
| `services/auth` | registro (hash + email de verificación, duplicados), login (éxito, credenciales incorrectas, bloqueado, pendiente), cambio de contraseña |
| `services/user` | perfil, inbox paginado, reenvío (permisos, estados), envío con plantilla, verificación por token (válido/expirado/inválido), CRUD admin, stats |
| `middlewares` | validación de JWT contra BD, bloqueo de usuarios no activos, restricción de rol admin |
| `app.main` | healthcheck y disponibilidad de Swagger |

## Convenciones

- Los tests de lógica asíncrona se escriben como `async def`; `pytest.ini`
  define `asyncio_mode = auto` para que pytest-asyncio los ejecute sin decorador.
- Cada archivo de test lleva un docstring con el módulo que cubre.
- Los fakes y helpers viven en `conftest.py`; si un fake solo lo usa un archivo,
  definirlo localmente ahí.
- No se requieren fixtures de red ni variables de entorno: el código de test
  debe correr igual en cualquier máquina y en CI.

## Añadir tests nuevos

1. Crear `tests/test_<modulo>.py` o ampliar un archivo existente.
2. Usar los fakes de `conftest.py`; si el módulo recibe una dependencia nueva,
  ampliar el fake correspondiente.
3. Ejecutar `pytest` y `flake8 tests` hasta dejarlos en verde.

## Jobs de CI (build_and_test.yaml)

El workflow ejecuta 5 jobs en paralelo (con caché de pip y cancelación de
runs duplicados de la misma rama):

| Job | Qué valida |
|---|---|
| `lint` | flake8: errores de sintaxis/undefined names (fallan) + lint completo informativo |
| `test` | pytest con cobertura: `--cov=app --cov-fail-under=75` y sube `coverage.xml` como artifact |
| `migrations` | PostgreSQL 16 real (servicio) + `alembic upgrade head` sobre BD fresca, `check_db_connection()` y `alembic current` |
| `smoke` | import de `app.main`, existencia de plantillas clave y `/health` con uvicorn real |
| `docker` | compila la imagen con `docker build` (sin push) |

El job `migrations` detecta migraciones rotas o no aplicables desde cero; el
job `test` falla si la cobertura baja del 75%.

## Notas de la implementación

- Se corrigieron imports internos rotos en `app/services/user_service.py`:
  `from models.email_model import ...` y `from core.security import ...`
  apuntaban a paquetes inexistentes (el paquete raíz es `app`). Ahora usan
  `from app.models...` y `from app.core...`.
- Se corrigió la migración inicial (`alembic/versions/20260413_000001`):
  `sa.Enum(..., create_type=False)` ignoraba silenciosamente `create_type`
  (no es un argumento del `Enum` genérico de SQLAlchemy), por lo que al crear
  la tabla `users` se emitía un `CREATE TYPE "userStatus"` duplicado y la
  migración fallaba en BD fresca. Se usa `postgresql.ENUM(..., create_type=False)`,
  que sí lo respeta.
- El workflow de CI usa Python 3.12 (antes 3.10) porque el código usa sintaxis
  PEP 701, e instala `requirements-dev.txt` para tener pytest, pytest-asyncio,
  pytest-cov, flake8 y httpx.
- `requirements-dev.txt` contiene las dependencias de desarrollo; las de
  producción siguen en `requirements.txt`.
