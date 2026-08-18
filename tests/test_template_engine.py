"""Tests unitarios del motor de plantillas (Jinja2 y Simple)."""

import pytest

from app.utils.template_engine import Jinja2TemplateEngine, SimpleTemplateEngine

TEMPLATES_DIR = "app/templates"


# ── Jinja2TemplateEngine ───────────────────────────────────

def test_render_replaces_context_variables():
    engine = Jinja2TemplateEngine(TEMPLATES_DIR)
    html = engine.render("welcome.html", {"nombre": "Ana"})
    assert "Ana" in html


def test_render_escapes_html_by_default():
    engine = Jinja2TemplateEngine(TEMPLATES_DIR)
    html = engine.render("welcome.html", {"nombre": "<script>alert(1)</script>"})
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_render_missing_template_raises_file_not_found():
    engine = Jinja2TemplateEngine(TEMPLATES_DIR)
    with pytest.raises(FileNotFoundError):
        engine.render("no-existe.html", {})


def test_list_templates_contains_known_templates():
    engine = Jinja2TemplateEngine(TEMPLATES_DIR)
    templates = engine.list_templates()
    assert "welcome.html" in templates
    assert "account_approved.html" in templates


def test_now_global_is_available():
    engine = Jinja2TemplateEngine(TEMPLATES_DIR)
    html = engine.render("welcome.html", {"nombre": "Ana"})
    assert html is not None


# ── SimpleTemplateEngine ───────────────────────────────────

def test_simple_engine_renders_with_format(tmp_path):
    (tmp_path / "saludo.txt").write_text("Hola {nombre}!", encoding="utf-8")
    engine = SimpleTemplateEngine(tmp_path)

    html = engine.render("saludo.txt", {"nombre": "Ana"})

    assert html == "Hola Ana!"


def test_simple_engine_missing_template_raises(tmp_path):
    engine = SimpleTemplateEngine(tmp_path)
    with pytest.raises(FileNotFoundError):
        engine.render("no-existe.html", {})
