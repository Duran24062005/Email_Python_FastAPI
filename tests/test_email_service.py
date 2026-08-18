"""Tests unitarios de app/services/email_services.py usando fakes."""

import io

from fastapi import UploadFile

from app.models.email_model import EmailStatus
from app.schemas.email_schema import EmailCreate, EmailUpdate
from app.services.email_services import EmailService

from tests.conftest import FakeEmailRepository, FakeSender, FakeTemplateEngine, make_email


def build_service(
    email_repo: FakeEmailRepository | None = None,
    sender: FakeSender | None = None,
    template_engine: FakeTemplateEngine | None = None,
) -> EmailService:
    return EmailService(
        repository=email_repo or FakeEmailRepository(),
        sender=sender or FakeSender(),
        template_engine=template_engine,
    )


def sample_email_create() -> EmailCreate:
    return EmailCreate(
        user_id=1,
        recipient="destino@example.com",
        subject="Hola mundo",
        body="Cuerpo en texto plano",
    )


# ── send_email ─────────────────────────────────────────────

async def test_send_email_plain_body_success(fake_email_repo, fake_sender):
    service = build_service(fake_email_repo, fake_sender)

    response = await service.send_email(sample_email_create())

    assert response.status == EmailStatus.SENT
    assert response.recipient == "destino@example.com"
    assert len(fake_sender.sent) == 1
    sent = fake_sender.sent[0]
    assert sent["recipient"] == "destino@example.com"
    assert sent["subject"] == "Hola mundo"
    assert sent["body"] == "Cuerpo en texto plano"


async def test_send_email_uses_provided_html_body(fake_email_repo, fake_sender):
    service = build_service(fake_email_repo, fake_sender)
    data = sample_email_create()
    data.html_body = "<html><body>HTML propio</body></html>"

    response = await service.send_email(data)

    assert response.status == EmailStatus.SENT
    assert fake_sender.sent[0]["html_body"] == "<html><body>HTML propio</body></html>"


async def test_send_email_renders_template(fake_email_repo, fake_sender, fake_template_engine):
    service = build_service(fake_email_repo, fake_sender, fake_template_engine)
    data = sample_email_create()
    data.template_name = "welcome.html"
    data.template_data = {"nombre": "Ana"}

    response = await service.send_email(data)

    assert fake_sender.sent[0]["html_body"] == "<html><body>rendered:welcome.html</body></html>"
    assert response.status == EmailStatus.SENT
    assert response.html_body == "<html><body>rendered:welcome.html</body></html>"


async def test_send_email_missing_template_falls_back_to_body(fake_email_repo, fake_sender):
    engine = FakeTemplateEngine(missing={"no-existe.html"})
    service = build_service(fake_email_repo, fake_sender, engine)
    data = sample_email_create()
    data.template_name = "no-existe.html"

    response = await service.send_email(data)

    assert response.status == EmailStatus.SENT
    assert fake_sender.sent[0]["html_body"] == (
        "<html><body>Cuerpo en texto plano</body></html>"
    )


async def test_send_email_sender_returns_false_marks_failed(fake_email_repo):
    service = build_service(fake_email_repo, FakeSender(result=False))

    response = await service.send_email(sample_email_create())

    assert response.status == EmailStatus.FAILED
    assert response.error_message == "Failed to send email"


async def test_send_email_sender_raises_marks_failed(fake_email_repo):
    service = build_service(fake_email_repo, FakeSender(error=RuntimeError("SMTP caído")))

    response = await service.send_email(sample_email_create())

    assert response.status == EmailStatus.FAILED
    assert response.error_message == "SMTP caído"


async def test_send_email_with_attachment(fake_email_repo, fake_sender):
    service = build_service(fake_email_repo, fake_sender)
    attachment = UploadFile(filename="reporte.pdf", file=io.BytesIO(b"%PDF-1.4 datos"))

    response = await service.send_email(sample_email_create(), attachment=attachment)

    assert response.status == EmailStatus.SENT
    assert fake_sender.sent[0]["attachment"] == b"%PDF-1.4 datos"
    assert fake_sender.sent[0]["attachment_filename"] == "reporte.pdf"


# ── get_email / get_all_emails ─────────────────────────────

async def test_get_email_found():
    repo = FakeEmailRepository([make_email(id=7, subject="Algo")])
    service = build_service(repo)

    email = await service.get_email(7)

    assert email is not None
    assert email.id == 7
    assert email.subject == "Algo"


async def test_get_email_not_found():
    service = build_service()
    assert await service.get_email(999) is None


async def test_get_all_emails_paginated():
    repo = FakeEmailRepository([
        make_email(id=1), make_email(id=2), make_email(id=3),
    ])
    service = build_service(repo)

    result = await service.get_all_emails(page=2, page_size=2)

    assert result.total == 3
    assert result.page == 2
    assert len(result.emails) == 1
    assert result.emails[0].id == 3


# ── update_email / delete_email ────────────────────────────

async def test_update_email_found():
    repo = FakeEmailRepository([make_email(id=1)])
    service = build_service(repo)

    updated = await service.update_email(1, EmailUpdate(status=EmailStatus.SENT))

    assert updated.status == EmailStatus.SENT


async def test_update_email_not_found():
    service = build_service()
    assert await service.update_email(999, EmailUpdate(status=EmailStatus.SENT)) is None


async def test_delete_email():
    repo = FakeEmailRepository([make_email(id=1)])
    service = build_service(repo)

    assert await service.delete_email(1) is True
    assert await service.delete_email(1) is False
