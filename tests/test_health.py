"""
Phase 1 — Backend tests: health endpoint, frontend routes, DB init, static assets.
"""

import pytest


class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        assert client.get("/api/health").status_code == 200

    def test_health_status_is_ok(self, client):
        assert client.get("/api/health").json()["status"] == "ok"

    def test_health_contains_version(self, client):
        data = client.get("/api/health").json()
        assert "version" in data and data["version"]

    def test_health_contains_environment(self, client):
        assert "environment" in client.get("/api/health").json()

    def test_health_method_not_allowed(self, client):
        assert client.post("/api/health").status_code == 405


class TestFrontendRoutes:
    def test_index_returns_200(self, client):
        assert client.get("/").status_code == 200

    def test_index_is_html(self, client):
        assert "text/html" in client.get("/").headers.get("content-type", "")

    def test_patient_page_returns_200(self, client):
        assert client.get("/patient").status_code == 200

    def test_guardian_page_returns_200(self, client):
        assert client.get("/guardian").status_code == 200

    def test_index_contains_echoaid(self, client):
        assert b"EchoAid" in client.get("/").content


class TestDatabaseInit:
    def test_tables_created(self):
        from backend.database import engine, init_db
        init_db()
        from sqlalchemy import inspect as sa_inspect
        tables = set(sa_inspect(engine).get_table_names())
        assert "categories" in tables
        assert "keywords" in tables
        assert "communication_preferences" in tables

    def test_init_db_idempotent(self):
        from backend.database import init_db
        init_db()
        init_db()


class TestStaticAssets:
    def test_tokens_css_served(self, client):
        assert client.get("/static/css/tokens.css").status_code == 200

    def test_base_css_served(self, client):
        assert client.get("/static/css/base.css").status_code == 200

    def test_app_js_served(self, client):
        assert client.get("/static/js/app.js").status_code == 200
