"""
Phase 4 — AI endpoint tests.

Tests:
  - /api/ai/status when AI is not configured
  - /api/ai/suggest returns 503 when not configured
  - Input validation (empty/too long fragments)
  - Suggestion parsing unit tests
  - Mocked successful AI call
"""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from backend.main import app
from backend.ai_service import _parse_suggestions


class TestAIStatus:
    def test_status_returns_200(self, client):
        r = client.get("/api/ai/status")
        assert r.status_code == 200

    def test_status_not_configured_when_no_key(self, client):
        # AI_API_KEY is empty (set in conftest.py)
        assert client.get("/api/ai/status").json()["configured"] is False

    def test_status_contains_model(self, client):
        assert "model" in client.get("/api/ai/status").json()

    def test_status_contains_message(self, client):
        assert "message" in client.get("/api/ai/status").json()


class TestAISuggestUnconfigured:
    def test_suggest_returns_503_when_not_configured(self, client):
        r = client.post("/api/ai/suggest", json={"fragments": "cold window"})
        assert r.status_code == 503

    def test_suggest_empty_fragments_fails_validation(self, client):
        r = client.post("/api/ai/suggest", json={"fragments": ""})
        assert r.status_code == 422

    def test_suggest_missing_body_fails_validation(self, client):
        r = client.post("/api/ai/suggest", json={})
        assert r.status_code == 422

    def test_suggest_too_long_fragments_fails(self, client):
        r = client.post("/api/ai/suggest", json={"fragments": "x" * 501})
        assert r.status_code == 422


class TestAISuggestMocked:
    """Tests with the Groq call mocked — no real network request."""

    def test_returns_suggestions_when_configured(self):
        mock_suggestions = [
            "I am feeling cold. Could you please close the window?",
            "It is cold in here. Would you mind closing the window?",
            "Please close the window, I am cold.",
        ]
        with patch(
            "backend.routers.ai.generate_suggestions",
            new=AsyncMock(return_value=mock_suggestions),
        ):
            with TestClient(app) as c:
                r = c.post("/api/ai/suggest",
                           json={"fragments": "cold + window + close"})
            assert r.status_code == 200
            data = r.json()
            assert len(data["suggestions"]) == 3
            assert data["fragments_received"] == "cold + window + close"
            assert "model" in data

    def test_suggestion_text_is_preserved(self):
        mock_suggestions = ["I need some water, please."]
        with patch(
            "backend.routers.ai.generate_suggestions",
            new=AsyncMock(return_value=mock_suggestions),
        ):
            with TestClient(app) as c:
                r = c.post("/api/ai/suggest", json={"fragments": "water"})
            assert r.json()["suggestions"][0] == "I need some water, please."


class TestSuggestionParsing:
    """Unit tests for the _parse_suggestions helper — no I/O needed."""

    def test_numbered_lines_parsed(self):
        text = "1. First sentence.\n2. Second sentence.\n3. Third sentence."
        result = _parse_suggestions(text)
        assert len(result) == 3

    def test_strips_numbering(self):
        text = "1. Hello world.\n2. Goodbye world."
        result = _parse_suggestions(text)
        assert not result[0].startswith("1.")
        assert result[0] == "Hello world."

    def test_empty_lines_skipped(self):
        text = "1. One.\n\n2. Two.\n\n\n3. Three."
        result = _parse_suggestions(text)
        assert len(result) == 3

    def test_max_3_returned(self):
        text = "\n".join(f"{i}. Sentence number {i}." for i in range(1, 6))
        result = _parse_suggestions(text)
        assert len(result) <= 3

    def test_fallback_for_unnumbered_text(self):
        text = "Just a plain sentence without numbering."
        result = _parse_suggestions(text)
        assert len(result) >= 1
        assert result[0] == text

    def test_paren_numbering_stripped(self):
        text = "1) First.\n2) Second.\n3) Third."
        result = _parse_suggestions(text)
        assert result[0] == "First."
