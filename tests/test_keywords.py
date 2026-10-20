"""
Phase 2/3 — Keyword CRUD, seed, and preferences tests.
"""

import pytest


def _make_kw(auth_client, label, message="Test message", **kwargs):
    payload = {"label": label, "message": message, **kwargs}
    r = auth_client.post("/api/keywords/", json=payload)
    assert r.status_code == 201, r.text
    return r.json()


class TestKeywordPublicRead:
    def test_list_keywords_public(self, client):
        r = client.get("/api/keywords/")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_list_urgent_public(self, client):
        r = client.get("/api/keywords/urgent")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_filter_by_category(self, auth_client, client):
        cat = auth_client.post("/api/categories/",
                               json={"name": "FilterCatKW"}).json()
        _make_kw(auth_client, "FilterKwLabel", "Filtered msg",
                 category_id=cat["id"])
        r = client.get(f"/api/keywords/?category_id={cat['id']}")
        assert r.status_code == 200
        assert any(kw["label"] == "FilterKwLabel" for kw in r.json())


class TestKeywordCRUD:
    def test_create_keyword(self, auth_client):
        kw = _make_kw(auth_client, "WaterKW", "I would like some water.")
        assert kw["label"] == "WaterKW"
        assert kw["is_enabled"] is True
        assert kw["is_urgent"] is False

    def test_create_urgent_keyword(self, auth_client):
        kw = _make_kw(auth_client, "HelpKW", "Please help me.", is_urgent=True)
        assert kw["is_urgent"] is True

    def test_create_keyword_blank_label_fails(self, auth_client):
        r = auth_client.post("/api/keywords/",
                             json={"label": "  ", "message": "msg"})
        assert r.status_code == 422

    def test_create_keyword_blank_message_fails(self, auth_client):
        r = auth_client.post("/api/keywords/",
                             json={"label": "lbl", "message": "  "})
        assert r.status_code == 422

    def test_update_keyword_label(self, auth_client):
        kw = _make_kw(auth_client, "OldLabelKW", "Msg")
        r = auth_client.patch(f"/api/keywords/{kw['id']}",
                              json={"label": "NewLabelKW"})
        assert r.status_code == 200
        assert r.json()["label"] == "NewLabelKW"

    def test_disable_keyword(self, auth_client):
        kw = _make_kw(auth_client, "DisableMeKW", "Msg")
        r = auth_client.patch(f"/api/keywords/{kw['id']}",
                              json={"is_enabled": False})
        assert r.status_code == 200
        assert r.json()["is_enabled"] is False

    def test_disabled_keyword_excluded_from_public(self, auth_client, client):
        kw = _make_kw(auth_client, "HiddenKwLabel", "Hidden msg")
        auth_client.patch(f"/api/keywords/{kw['id']}",
                          json={"is_enabled": False})
        public = client.get("/api/keywords/").json()
        assert not any(k["id"] == kw["id"] for k in public)

    def test_delete_keyword(self, auth_client):
        kw = _make_kw(auth_client, "DeleteMeKW", "Gone")
        r = auth_client.delete(f"/api/keywords/{kw['id']}")
        assert r.status_code == 204

    def test_delete_nonexistent_keyword(self, auth_client):
        r = auth_client.delete("/api/keywords/99999")
        assert r.status_code == 404

    def test_get_keyword_by_id(self, auth_client):
        kw = _make_kw(auth_client, "GetByIdKW", "Find me")
        r = auth_client.get(f"/api/keywords/{kw['id']}")
        assert r.status_code == 200
        assert r.json()["id"] == kw["id"]

    def test_get_nonexistent_keyword(self, client):
        r = client.get("/api/keywords/99999")
        assert r.status_code == 404

    def test_list_all_keywords_guardian_only(self, auth_client):
        r = auth_client.get("/api/keywords/all")
        assert r.status_code == 200

    def test_list_all_keywords_unauthenticated_fails(self, client):
        r = client.get("/api/keywords/all")
        assert r.status_code == 401

    def test_urgent_keywords_appear_in_urgent_list(self, auth_client, client):
        kw = _make_kw(auth_client, "UrgentVisibleKW", "Urgent!", is_urgent=True)
        urgent = client.get("/api/keywords/urgent").json()
        assert any(k["id"] == kw["id"] for k in urgent)


class TestSeed:
    def test_seed_creates_categories_and_keywords(self, auth_client):
        r = auth_client.post("/api/keywords/seed")
        assert r.status_code == 201
        data = r.json()
        assert "categories_created" in data
        assert "keywords_created" in data

    def test_seed_is_idempotent(self, auth_client):
        # Run once to ensure data exists, then run again
        auth_client.post("/api/keywords/seed")
        r2 = auth_client.post("/api/keywords/seed").json()
        assert r2["categories_created"] == 0
        assert r2["keywords_created"] == 0

    def test_seeded_phrases_appear_in_public_list(self, auth_client, client):
        auth_client.post("/api/keywords/seed")
        keywords = client.get("/api/keywords/").json()
        labels = {kw["label"] for kw in keywords}
        # At least one of these seed phrases must be present
        assert labels & {"Help", "Water", "Stop", "Happy"}


class TestPreferences:
    def test_get_default_preferences(self, client):
        r = client.get("/api/preferences/")
        assert r.status_code == 200
        data = r.json()
        assert "speech_rate" in data
        assert "large_text" in data
        assert "speak_on_select" in data

    def test_update_preferences_guardian_only(self, auth_client):
        r = auth_client.patch("/api/preferences/",
                              json={"large_text": True, "speech_rate": 120})
        assert r.status_code == 200
        assert r.json()["large_text"] is True
        assert r.json()["speech_rate"] == 120

    def test_speech_rate_out_of_range_fails(self, auth_client):
        r = auth_client.patch("/api/preferences/", json={"speech_rate": 999})
        assert r.status_code == 422
