"""
Fixtures y fakes compartidos por toda la suite de tests.

Estrategia:
- Los tests de repositorios usan una base SQLite en memoria (misma API que
  SQLAlchemy, sin necesidad de PostgreSQL).
- Los tests de servicios usan fakes (repositorios, sender, template engine)
  implementados con estructuras en memoria, siguiendo el principio de
  inversión de dependencias que ya aplica el proyecto.
"""

from datetime import UTC, datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config.database.base import Base
import app.models  # noqa: F401  (registra los modelos en Base.metadata)

from app.models.user_models import User, UserRole, UserStatus
from app.models.email_model import Email, EmailStatus
from app.schemas.user_schemas import UserCreate, UserUpdate
from app.schemas.email_schema import EmailCreate, EmailUpdate


# ═══════════════════════════════════════════════════════════
# BASE SQLite EN MEMORIA (tests de repositorios)
# ═══════════════════════════════════════════════════════════

@pytest.fixture
def db_session():
    """Sesión SQLAlchemy sobre SQLite en memoria, con esquema creado."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


# ═══════════════════════════════════════════════════════════
# HELPERS PARA CONSTRUIR OBJETOS DE DOMINIO
# ═══════════════════════════════════════════════════════════

def make_user(**overrides) -> User:
    """Construye un User con valores por defecto y permite sobrescribirlos."""
    now = datetime.now(UTC).replace(tzinfo=None)
    defaults = dict(
        id=1,
        name="Juan Pérez",
        email="juan@example.com",
        hash_password="hashed-not-a-real-hash",
        email_key=None,
        status=UserStatus.ACTIVE,
        role=UserRole.GENERAL,
        last_login=None,
        email_verify=False,
        created_at=now,
        updated_at=now,
    )
    defaults.update(overrides)
    return User(**defaults)


def make_email(**overrides) -> Email:
    """Construye un Email con valores por defecto y permite sobrescribirlos."""
    now = datetime.now(UTC).replace(tzinfo=None)
    defaults = dict(
        id=1,
        user_id=1,
        recipient="destino@example.com",
        subject="Asunto de prueba",
        body="Cuerpo de prueba",
        html_body=None,
        status=EmailStatus.PENDING,
        error_message=None,
        sent_at=None,
        created_at=now,
        updated_at=now,
    )
    defaults.update(overrides)
    return Email(**defaults)


# ═══════════════════════════════════════════════════════════
# FAKES DE REPOSITORIOS (para tests de servicios)
# ═══════════════════════════════════════════════════════════

class FakeUserRepository:
    """Repositorio de usuarios en memoria con la misma interfaz que IUserRepository."""

    def __init__(self, users: list[User] | None = None):
        self.users: dict[int, User] = {}
        self._next_id = 1
        for user in users or []:
            self._store(user)

    def _store(self, user: User) -> User:
        user.id = user.id or self._next_id
        self._next_id = max(self._next_id, user.id + 1)
        self.users[user.id] = user
        return user

    async def get_by_id(self, user_id: int) -> User | None:
        return self.users.get(user_id)

    async def get_by_email(self, email: str) -> User | None:
        for user in self.users.values():
            if user.email == email:
                return user
        return None

    async def create_with_hash(self, name: str, email: str, hashed_password: str) -> User:
        return self._store(make_user(
            id=self._next_id, name=name, email=email, hash_password=hashed_password
        ))

    async def create(self, user_data: UserCreate) -> User:
        return self._store(make_user(
            id=self._next_id,
            name=user_data.name,
            email=user_data.email,
            hash_password=user_data.password,
        ))

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        return list(self.users.values())[skip: skip + limit]

    async def get_pending_users(self) -> list[User]:
        return [u for u in self.users.values() if u.status == UserStatus.PENDING]

    async def update(self, user_id: int, user_data: UserUpdate) -> User | None:
        user = await self.get_by_id(user_id)
        if not user:
            return None
        for field, value in user_data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        user.updated_at = datetime.now(UTC).replace(tzinfo=None)
        return user

    async def update_status(self, user_id: int, new_status: UserStatus) -> User | None:
        user = await self.get_by_id(user_id)
        if not user:
            return None
        user.status = new_status
        user.updated_at = datetime.now(UTC).replace(tzinfo=None)
        return user

    async def update_email_key(self, user_id: int, email_key: str) -> None:
        user = await self.get_by_id(user_id)
        if user:
            user.email_key = email_key

    async def set_email_verified(self, user_id: int) -> None:
        user = await self.get_by_id(user_id)
        if user:
            user.email_verify = True

    async def update_last_login(self, user_id: int) -> None:
        user = await self.get_by_id(user_id)
        if user:
            user.last_login = datetime.now(UTC).replace(tzinfo=None)

    async def update_password(self, user_id: int, hashed_password: str) -> None:
        user = await self.get_by_id(user_id)
        if user:
            user.hash_password = hashed_password

    async def delete(self, user_id: int) -> bool:
        return self.users.pop(user_id, None) is not None

    async def count(self) -> int:
        return len(self.users)


class FakeEmailRepository:
    """Repositorio de emails en memoria con la misma interfaz que IEmailRepository."""

    def __init__(self, emails: list[Email] | None = None):
        self.emails: dict[int, Email] = {}
        self._next_id = 1
        for email in emails or []:
            self._store(email)

    def _store(self, email: Email) -> Email:
        email.id = email.id or self._next_id
        self._next_id = max(self._next_id, email.id + 1)
        self.emails[email.id] = email
        return email

    async def create(self, email_data: EmailCreate) -> Email:
        return self._store(make_email(
            id=self._next_id,
            user_id=email_data.user_id,
            recipient=email_data.recipient,
            subject=email_data.subject,
            body=email_data.body,
            html_body=email_data.html_body,
        ))

    async def get_by_id(self, email_id: int) -> Email | None:
        return self.emails.get(email_id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Email]:
        return list(self.emails.values())[skip: skip + limit]

    async def get_by_user_id(self, user_id: int, skip: int = 0, limit: int = 10) -> list[Email]:
        mine = sorted(
            (e for e in self.emails.values() if e.user_id == user_id),
            key=lambda e: e.created_at,
            reverse=True,
        )
        return mine[skip: skip + limit]

    async def count_by_user(self, user_id: int) -> int:
        return sum(1 for e in self.emails.values() if e.user_id == user_id)

    async def update(self, email_id: int, email_data: EmailUpdate) -> Email | None:
        email = await self.get_by_id(email_id)
        if not email:
            return None
        for field, value in email_data.model_dump(exclude_unset=True).items():
            setattr(email, field, value)
        email.updated_at = datetime.now(UTC).replace(tzinfo=None)
        return email

    async def delete(self, email_id: int) -> bool:
        return self.emails.pop(email_id, None) is not None

    async def count(self) -> int:
        return len(self.emails)

    async def update_status(
        self, email_id: int, status: EmailStatus, error_message: str | None = None
    ) -> Email | None:
        email = await self.get_by_id(email_id)
        if not email:
            return None
        email.status = status
        email.error_message = error_message
        if status == EmailStatus.SENT:
            email.sent_at = datetime.now(UTC).replace(tzinfo=None)
        return email


# ═══════════════════════════════════════════════════════════
# FAKES DE INFRAESTRUCTURA (sender y template engine)
# ═══════════════════════════════════════════════════════════

class FakeSender:
    """Sender que registra los envíos y permite configurar resultado/errores."""

    def __init__(self, result: bool = True, error: Exception | None = None):
        self.result = result
        self.error = error
        self.sent: list[dict] = []

    async def send(
        self,
        recipient: str,
        subject: str,
        body: str,
        html_body: str | None = None,
        attachment: bytes | None = None,
        attachment_filename: str | None = None,
    ) -> bool:
        if self.error:
            raise self.error
        self.sent.append({
            "recipient": recipient,
            "subject": subject,
            "body": body,
            "html_body": html_body,
            "attachment": attachment,
            "attachment_filename": attachment_filename,
        })
        return self.result


class FakeTemplateEngine:
    """Template engine que renderiza a un HTML simple y puede fallar si falta la plantilla."""

    def __init__(self, missing: set[str] | None = None):
        self.missing = missing or set()
        self.rendered: list[tuple[str, dict]] = []

    def render(self, template_name: str, context: dict) -> str:
        if template_name in self.missing:
            raise FileNotFoundError(f"Template '{template_name}' not found")
        self.rendered.append((template_name, context))
        return f"<html><body>rendered:{template_name}</body></html>"


@pytest.fixture
def fake_user_repo():
    return FakeUserRepository()


@pytest.fixture
def fake_email_repo():
    return FakeEmailRepository()


@pytest.fixture
def fake_sender():
    return FakeSender()


@pytest.fixture
def fake_template_engine():
    return FakeTemplateEngine()
