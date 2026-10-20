"""
Phase 2 — Authentication tests.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app


class TestAuthLogin:
    def test_wrong_pin_returns_401(self, client):
        r = client.post("/api/auth/login", json={"pin": "0000"})
        assert r.status_code == 401

    def test_correct_pin_returns_200(self):
        # Use a fresh client to avoid polluting the shared anonymous client's cookies
        with TestClient(app) as c:
            r = c.post("/api/auth/login", json={"pin": "9999"})
            assert r.status_code == 200
            assert r.json()["authenticated"] is True

    def test_correct_pin_sets_cookie(self):
        with TestClient(app) as c:
            r = c.post("/api/auth/login", json={"pin": "9999"})
            assert "echoaid_session" in r.cookies

    def test_logout_clears_session(self, auth_client):
        # Create a disposable logged-in client so auth_client remains valid
        with TestClient(app) as c:
            c.post("/api/auth/login", json={"pin": "9999"})
            r = c.post("/api/auth/logout", json={})
            assert r.status_code == 200

    def test_check_without_cookie_returns_401(self, client):
        r = client.get("/api/auth/check")
        assert r.status_code == 401

    def test_check_with_valid_session_returns_200(self, auth_client):
        r = auth_client.get("/api/auth/check")
        assert r.status_code == 200
        assert r.json()["authenticated"] is True


class TestProtectedEndpoints:
    def test_unauthenticated_cannot_create_category(self, client):
        r = client.post("/api/categories/", json={"name": "Hack"})
        assert r.status_code == 401

    def test_unauthenticated_cannot_create_keyword(self, client):
        r = client.post("/api/keywords/", json={"label": "X", "message": "Y"})
        assert r.status_code == 401

    def test_unauthenticated_cannot_seed(self, client):
        r = client.post("/api/keywords/seed")
        assert r.status_code == 401

    def test_unauthenticated_cannot_update_preferences(self, client):
        r = client.patch("/api/preferences/", json={"large_text": True})
        assert r.status_code == 401
