"""
Phase 1 — Backend tests.

Tests the health endpoint and database initialization.
Run with:  pytest tests/ -v
"""

import os
import pytest
from fastapi.testclient import TestClient


# Use an in-memory SQLite database for tests so the test run never touches
# the development database file.
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("APP_ENV", "testing")


from backend.main import app  # noqa: E402  (must come after env vars are set)


@pytest.fixture(scope="module")
def client():
    """Return a TestClient with the application lifespan (startup) executed."""
    with TestClient(app) as c:
        yield c


# ──────────────────────────────────────────────────────────────────────
# Health endpoint
# ──────────────────────────────────────────────────────────────────────

class TestHealthEndpoint:

    def test_health_returns_200(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200

    def test_health_status_is_ok(self, client):
        data = client.get("/api/health").json()
        assert data["status"] == "ok"

    def test_health_contains_version(self, client):
        data = client.get("/api/health").json()
        assert "version" in data
        assert data["version"]   # non-empty string

    def test_health_contains_environment(self, client):
        data = client.get("/api/health").json()
        assert "environment" in data

    def test_health_method_not_allowed(self, client):
        response = client.post("/api/health")
        assert response.status_code == 405


# ──────────────────────────────────────────────────────────────────────
# Frontend pages
# ──────────────────────────────────────────────────────────────────────

class TestFrontendRoutes:

    def test_index_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_index_is_html(self, client):
        response = client.get("/")
        assert "text/html" in response.headers.get("content-type", "")

    def test_patient_page_returns_200(self, client):
        response = client.get("/patient")
        assert response.status_code == 200

    def test_guardian_page_returns_200(self, client):
        response = client.get("/guardian")
        assert response.status_code == 200

    def test_index_contains_echoaid(self, client):
        response = client.get("/")
        assert b"EchoAid" in response.content


# ──────────────────────────────────────────────────────────────────────
# Database initialization
# ──────────────────────────────────────────────────────────────────────

class TestDatabaseInit:

    def test_tables_created(self):
        """Verify that all expected tables exist after init_db."""
        from backend.database import engine, init_db
        init_db()

        from sqlalchemy import inspect as sa_inspect
        inspector = sa_inspect(engine)
        tables = set(inspector.get_table_names())

        assert "categories" in tables
        assert "keywords" in tables
        assert "communication_preferences" in tables

    def test_init_db_idempotent(self):
        """Calling init_db() twice must not raise an error."""
        from backend.database import init_db
        init_db()  # first call
        init_db()  # second call — should be a no-op


# ──────────────────────────────────────────────────────────────────────
# Static assets
# ──────────────────────────────────────────────────────────────────────

class TestStaticAssets:

    def test_tokens_css_served(self, client):
        response = client.get("/static/css/tokens.css")
        assert response.status_code == 200

    def test_base_css_served(self, client):
        response = client.get("/static/css/base.css")
        assert response.status_code == 200

    def test_app_js_served(self, client):
        response = client.get("/static/js/app.js")
        assert response.status_code == 200
