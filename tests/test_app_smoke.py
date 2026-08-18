"""Smoke tests de la aplicación FastAPI (no requieren base de datos)."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_healthcheck_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["app"] == "Email_Python_FastAPI"


def test_root_redirects_to_docs():
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (302, 307)
    assert "/docs" in response.headers["location"]


def test_docs_available():
    response = client.get("/docs")
    assert response.status_code == 200
