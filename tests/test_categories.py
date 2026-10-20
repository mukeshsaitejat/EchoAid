"""
Phase 2 — Category CRUD tests.
"""

import pytest


class TestCategoryPublicRead:
    def test_list_enabled_categories(self, client):
        r = client.get("/api/categories/")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_preferences_readable_publicly(self, client):
        r = client.get("/api/preferences/")
        assert r.status_code == 200


class TestCategoryCRUD:
    def test_create_category(self, auth_client):
        r = auth_client.post("/api/categories/",
                             json={"name": "TestCatUnique1"})
        assert r.status_code == 201
        assert r.json()["name"] == "TestCatUnique1"

    def test_create_duplicate_category_fails(self, auth_client):
        auth_client.post("/api/categories/", json={"name": "DupCat123"})
        r = auth_client.post("/api/categories/", json={"name": "DupCat123"})
        assert r.status_code == 409

    def test_update_category(self, auth_client):
        created = auth_client.post("/api/categories/",
                                   json={"name": "OldNameXYZ"}).json()
        r = auth_client.patch(f"/api/categories/{created['id']}",
                              json={"name": "NewNameXYZ"})
        assert r.status_code == 200
        assert r.json()["name"] == "NewNameXYZ"

    def test_delete_empty_category(self, auth_client):
        created = auth_client.post("/api/categories/",
                                   json={"name": "ToDeleteXYZ"}).json()
        r = auth_client.delete(f"/api/categories/{created['id']}")
        assert r.status_code == 204

    def test_delete_nonexistent_category_returns_404(self, auth_client):
        r = auth_client.delete("/api/categories/99999")
        assert r.status_code == 404

    def test_cannot_delete_category_with_keywords(self, auth_client):
        cat = auth_client.post("/api/categories/",
                               json={"name": "HasKwCat"}).json()
        auth_client.post("/api/keywords/",
                         json={"label": "KwForCat", "message": "MsgX",
                               "category_id": cat["id"]})
        r = auth_client.delete(f"/api/categories/{cat['id']}")
        assert r.status_code == 409
        assert "keyword" in r.json()["detail"].lower()

    def test_get_category_with_keywords(self, auth_client):
        cat = auth_client.post("/api/categories/",
                               json={"name": "WithKwsCat"}).json()
        auth_client.post("/api/keywords/",
                         json={"label": "KW-A", "message": "Msg-A",
                               "category_id": cat["id"]})
        r = auth_client.get(f"/api/categories/{cat['id']}")
        assert r.status_code == 200
        assert len(r.json()["keywords"]) >= 1

    def test_list_all_categories_guardian_only(self, auth_client):
        r = auth_client.get("/api/categories/all")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_get_nonexistent_category_returns_404(self, client):
        r = client.get("/api/categories/99999")
        assert r.status_code == 404
