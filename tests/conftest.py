"""
Shared pytest configuration and fixtures.

Key design decisions:
1. All environment variables are set before any backend import.
2. A fresh file-based SQLite test DB is created at session start and
   deleted at session end, giving us a clean slate every run.
3. A single anonymous TestClient and a single authenticated guardian
   TestClient are shared across the whole test session.
"""

import os
import pathlib

# ── Wipe any leftover DB from a previous run (do this FIRST) ──────────
_TEST_DB_FILE = pathlib.Path("test_echoaid.db")
if _TEST_DB_FILE.exists():
    try:
        _TEST_DB_FILE.unlink()
    except OSError:
        pass

# ── Environment variables MUST be set before any backend import ───────
os.environ["DATABASE_URL"]  = f"sqlite:///./{_TEST_DB_FILE.name}"
os.environ["APP_ENV"]       = "testing"
os.environ["GUARDIAN_PIN"]  = "9999"
os.environ["SECRET_KEY"]    = "test-secret-key-do-not-use-in-production"
os.environ["AI_API_KEY"]    = ""

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from backend.main import app  # noqa: E402
from backend.database import init_db  # noqa: E402

# Create all tables once before any test runs
init_db()


# ── Fixtures ───────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def client():
    """Anonymous TestClient — shared across the whole test session."""
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def auth_client():
    """
    Guardian-authenticated TestClient.
    Logs in once at session start; the cookie persists.
    """
    with TestClient(app) as c:
        r = c.post("/api/auth/login", json={"pin": "9999"})
        assert r.status_code == 200, (
            f"Guardian login failed in fixture: {r.status_code} — {r.text}"
        )
        yield c


def pytest_sessionfinish(session, exitstatus):
    """Delete the test DB after the run completes."""
    if _TEST_DB_FILE.exists():
        try:
            _TEST_DB_FILE.unlink()
        except OSError:
            pass
