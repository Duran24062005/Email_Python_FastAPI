"""Tests de los repositorios SQLAlchemy usando SQLite en memoria.

SQLite implementa la misma API de sesión de SQLAlchemy que PostgreSQL,
por lo que permite probar la lógica de acceso a datos sin base externa.
"""

from datetime import datetime, timedelta

from app.models.user_models import UserRole, UserStatus
from app.models.email_model import EmailStatus
from app.repositories.user_repository import UserRepository
from app.repositories.email_repository import EmailRepository
from app.schemas.user_schemas import UserCreate, UserUpdate
from app.schemas.email_schema import EmailCreate, EmailUpdate


# ── UserRepository ─────────────────────────────────────────

async def test_user_repository_create(db_session):
    repo = UserRepository(db_session)
    user = await repo.create(UserCreate(
        name="Ana", email="ana@example.com", password="plain-password"
    ))
    assert user.id is not None
    assert user.role == UserRole.GENERAL
    assert user.status == UserStatus.ACTIVE
    assert user.email_verify is False


async def test_user_repository_create_with_hash(db_session):
    repo = UserRepository(db_session)
    user = await repo.create_with_hash(
        name="Ana", email="ana@example.com", hashed_password="$2b$hash"
    )
    assert user.id is not None
    assert user.hash_password == "$2b$hash"


async def test_user_repository_get_by_id_and_email(db_session):
    repo = UserRepository(db_session)
    created = await repo.create_with_hash("Ana", "ana@example.com", "hash")

    by_id = await repo.get_by_id(created.id)
    by_email = await repo.get_by_email("ana@example.com")

    assert by_id is not None and by_id.id == created.id
    assert by_email is not None and by_email.id == created.id
    assert await repo.get_by_id(9999) is None
    assert await repo.get_by_email("nadie@example.com") is None


async def test_user_repository_get_all_with_pagination(db_session):
    repo = UserRepository(db_session)
    for i in range(5):
        await repo.create_with_hash(f"User {i}", f"user{i}@example.com", "hash")

    first_page = await repo.get_all(skip=0, limit=2)
    second_page = await repo.get_all(skip=2, limit=2)

    assert len(first_page) == 2
    assert len(second_page) == 2
    assert {u.id for u in first_page}.isdisjoint({u.id for u in second_page})


async def test_user_repository_get_pending_users(db_session):
    repo = UserRepository(db_session)
    active = await repo.create_with_hash("Ana", "ana@example.com", "hash")
    pending = await repo.create_with_hash("Bob", "bob@example.com", "hash")
    await repo.update_status(pending.id, UserStatus.PENDING)

    pending_users = await repo.get_pending_users()
    assert pending_users == [pending]
    assert active.id not in {u.id for u in pending_users}


async def test_user_repository_update(db_session):
    repo = UserRepository(db_session)
    user = await repo.create_with_hash("Ana", "ana@example.com", "hash")

    updated = await repo.update(user.id, UserUpdate(name="Ana María"))
    assert updated.name == "Ana María"

    assert await repo.update(9999, UserUpdate(name="X")) is None


async def test_user_repository_update_status(db_session):
    repo = UserRepository(db_session)
    user = await repo.create_with_hash("Ana", "ana@example.com", "hash")

    updated = await repo.update_status(user.id, UserStatus.BLOCKED)
    assert updated.status == UserStatus.BLOCKED
    assert await repo.update_status(9999, UserStatus.BLOCKED) is None


async def test_user_repository_email_key_and_verification(db_session):
    repo = UserRepository(db_session)
    user = await repo.create_with_hash("Ana", "ana@example.com", "hash")

    await repo.update_email_key(user.id, "xxxx xxxx")
    await repo.set_email_verified(user.id)

    refreshed = await repo.get_by_id(user.id)
    assert refreshed.email_key == "xxxx xxxx"
    assert refreshed.email_verify is True


async def test_user_repository_update_last_login_and_password(db_session):
    repo = UserRepository(db_session)
    user = await repo.create_with_hash("Ana", "ana@example.com", "hash")

    await repo.update_last_login(user.id)
    await repo.update_password(user.id, "nuevo-hash")

    refreshed = await repo.get_by_id(user.id)
    assert refreshed.last_login is not None
    assert refreshed.hash_password == "nuevo-hash"


async def test_user_repository_delete(db_session):
    repo = UserRepository(db_session)
    user = await repo.create_with_hash("Ana", "ana@example.com", "hash")

    assert await repo.delete(user.id) is True
    assert await repo.delete(user.id) is False
    assert await repo.get_by_id(user.id) is None


async def test_user_repository_count(db_session):
    repo = UserRepository(db_session)
    assert await repo.count() == 0
    await repo.create_with_hash("Ana", "ana@example.com", "hash")
    await repo.create_with_hash("Bob", "bob@example.com", "hash")
    assert await repo.count() == 2


# ── EmailRepository ────────────────────────────────────────

async def test_email_repository_create(db_session):
    repo = EmailRepository(db_session)
    email = await repo.create(EmailCreate(
        user_id=1, recipient="d@example.com", subject="Hola", body="Cuerpo"
    ))
    assert email.id is not None
    assert email.status == EmailStatus.PENDING
    assert email.created_at is not None


async def test_email_repository_get_by_id(db_session):
    repo = EmailRepository(db_session)
    created = await repo.create(EmailCreate(
        user_id=1, recipient="d@example.com", subject="Hola"
    ))
    assert (await repo.get_by_id(created.id)).id == created.id
    assert await repo.get_by_id(9999) is None


async def test_email_repository_get_all(db_session):
    repo = EmailRepository(db_session)
    for i in range(3):
        await repo.create(EmailCreate(
            user_id=1, recipient=f"d{i}@example.com", subject=f"Tema {i}"
        ))
    emails = await repo.get_all(skip=0, limit=2)
    assert len(emails) == 2


async def test_email_repository_get_by_user_id_orders_by_date_desc(db_session):
    repo = EmailRepository(db_session)
    first = await repo.create(EmailCreate(
        user_id=1, recipient="a@example.com", subject="Primero"
    ))
    second = await repo.create(EmailCreate(
        user_id=1, recipient="b@example.com", subject="Segundo"
    ))
    await repo.create(EmailCreate(
        user_id=2, recipient="otro@example.com", subject="De otro usuario"
    ))

    # Controlar fechas para verificar el orden descendente
    first.created_at = datetime.utcnow() - timedelta(hours=2)
    second.created_at = datetime.utcnow()
    db_session.commit()

    inbox = await repo.get_by_user_id(1)
    assert [e.subject for e in inbox] == ["Segundo", "Primero"]

    paged = await repo.get_by_user_id(1, skip=1, limit=10)
    assert [e.subject for e in paged] == ["Primero"]


async def test_email_repository_count_by_user(db_session):
    repo = EmailRepository(db_session)
    await repo.create(EmailCreate(user_id=1, recipient="a@example.com", subject="1"))
    await repo.create(EmailCreate(user_id=1, recipient="b@example.com", subject="2"))
    await repo.create(EmailCreate(user_id=2, recipient="c@example.com", subject="3"))

    assert await repo.count_by_user(1) == 2
    assert await repo.count_by_user(2) == 1
    assert await repo.count() == 3


async def test_email_repository_update(db_session):
    repo = EmailRepository(db_session)
    email = await repo.create(EmailCreate(
        user_id=1, recipient="a@example.com", subject="Antes"
    ))
    updated = await repo.update(email.id, EmailUpdate(status=EmailStatus.SENT))
    assert updated.status == EmailStatus.SENT
    assert await repo.update(9999, EmailUpdate(status=EmailStatus.SENT)) is None


async def test_email_repository_update_status(db_session):
    repo = EmailRepository(db_session)
    email = await repo.create(EmailCreate(
        user_id=1, recipient="a@example.com", subject="Hola"
    ))

    sent = await repo.update_status(email.id, EmailStatus.SENT)
    assert sent.status == EmailStatus.SENT
    assert sent.sent_at is not None

    failed = await repo.update_status(email.id, EmailStatus.FAILED, "SMTP error")
    assert failed.status == EmailStatus.FAILED
    assert failed.error_message == "SMTP error"

    assert await repo.update_status(9999, EmailStatus.FAILED) is None


async def test_email_repository_delete(db_session):
    repo = EmailRepository(db_session)
    email = await repo.create(EmailCreate(
        user_id=1, recipient="a@example.com", subject="Hola"
    ))
    assert await repo.delete(email.id) is True
    assert await repo.delete(email.id) is False
