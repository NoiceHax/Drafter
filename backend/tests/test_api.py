"""Critical API endpoint tests with an overridden auth dependency.

These run against the real database but clean up the projects/users they create.
The `current_user` dependency is overridden so requests are authenticated as a
dedicated throwaway test user.
"""
from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from app.api import deps
from app.db.session import SessionLocal, get_db
from app.main import app
from app.models.models import User
from tests.conftest import FakeLLM


def _make_user(email: str) -> User:
    db = SessionLocal()
    try:
        u = User(email=email, display_name="Tester", is_alpha=True)
        db.add(u)
        db.commit()
        db.refresh(u)
        return u
    finally:
        db.close()


def _delete_user(user_id) -> None:
    db = SessionLocal()
    try:
        u = db.get(User, user_id)
        if u:
            db.delete(u)
            db.commit()
    finally:
        db.close()


@pytest.fixture
def test_user():
    u = _make_user(f"apitest-{uuid.uuid4().hex[:8]}@example.com")
    yield u
    _delete_user(u.id)


@pytest.fixture
def client(test_user):
    # Authenticate every request as the throwaway test user.
    app.dependency_overrides[deps.current_user] = lambda: test_user
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_projects_require_auth():
    # No override here: a bare client must be rejected.
    app.dependency_overrides.clear()
    bare = TestClient(app)
    r = bare.get("/api/projects")
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "unauthorized"


def test_project_crud_roundtrip(client):
    r = client.post("/api/projects", json={
        "idea": "endpoint test project", "initial_keywords": ["x"],
        "platform": "tiktok", "target_duration_seconds": 30, "tone": "educational",
    })
    assert r.status_code == 201
    pid = r.json()["id"]
    try:
        d = client.get(f"/api/projects/{pid}")
        assert d.status_code == 200
        body = d.json()
        assert body["idea"] == "endpoint test project"
        assert isinstance(body["research_enabled"], bool)
        assert len(body["keywords"]) == 1

        p = client.patch(f"/api/projects/{pid}", json={"title": "Renamed"})
        assert p.json()["title"] == "Renamed"
    finally:
        assert client.delete(f"/api/projects/{pid}").status_code == 204


def test_missing_project_returns_404(client):
    r = client.get("/api/projects/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "not_found"


def test_projects_are_isolated_per_user(client, test_user):
    # Create a project owned by test_user.
    pid = client.post("/api/projects", json={
        "idea": "owned by user A", "platform": "generic",
        "target_duration_seconds": 60, "tone": "conversational",
    }).json()["id"]
    try:
        # A second user must not see it in their list, nor fetch it by id.
        other = _make_user(f"other-{uuid.uuid4().hex[:8]}@example.com")
        try:
            app.dependency_overrides[deps.current_user] = lambda: other
            others = client.get("/api/projects").json()
            assert all(p["id"] != pid for p in others)
            assert client.get(f"/api/projects/{pid}").status_code == 404
        finally:
            app.dependency_overrides[deps.current_user] = lambda: test_user
            _delete_user(other.id)
    finally:
        client.delete(f"/api/projects/{pid}")


def test_keyword_recommend_endpoint_with_overridden_llm(client):
    fake = FakeLLM({
        "KeywordRecListOut": {"recommendations": [
            {"keyword": "AI chip war", "category": "story", "reason": "conflict", "relevance_score": 0.9},
        ]}
    })
    from app.services.keyword_service import KeywordService

    def override():
        gen = get_db()
        db = next(gen)
        try:
            yield KeywordService(db, fake)
        finally:
            gen.close()

    app.dependency_overrides[deps.keyword_service] = override

    r = client.post("/api/projects", json={
        "idea": "kw test", "platform": "generic", "target_duration_seconds": 60, "tone": "conversational",
    })
    pid = r.json()["id"]
    try:
        rec = client.post(f"/api/projects/{pid}/keywords/recommend", json={})
        assert rec.status_code == 200
        data = rec.json()
        assert data[0]["keyword"] == "AI chip war"
    finally:
        client.delete(f"/api/projects/{pid}")
