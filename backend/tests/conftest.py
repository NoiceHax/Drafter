"""Shared test fixtures.

Service/endpoint tests run against the configured Postgres database inside a
transaction that is rolled back after each test, so no test data persists.
"""
from __future__ import annotations

import pytest
from sqlalchemy.orm import Session

from app.db.session import SessionLocal, engine
from app.models.models import User
from app.providers.llm.base import ChatMessage, LLMProvider


@pytest.fixture
def db() -> Session:
    """A session bound to a connection whose transaction is rolled back."""
    connection = engine.connect()
    trans = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    try:
        yield session
    finally:
        session.close()
        trans.rollback()
        connection.close()


@pytest.fixture
def user(db) -> User:
    """A persisted test user (rolled back with the transaction)."""
    import uuid

    u = User(email=f"test-{uuid.uuid4().hex[:8]}@example.com", display_name="Tester")
    db.add(u)
    db.flush()
    return u


class FakeLLM(LLMProvider):
    """Deterministic LLM used in service tests; returns canned structured output."""

    def __init__(self, responses: dict[str, dict] | None = None):
        self.responses = responses or {}
        self.calls: list[str] = []

    def generate(self, messages, *, temperature=0.7, max_tokens=None):
        return "text"

    def stream(self, messages, *, temperature=0.7, max_tokens=None):
        yield "text"

    def generate_structured(self, messages, schema, *, temperature=0.4, max_tokens=None):
        self.calls.append(schema.__name__)
        data = self.responses.get(schema.__name__)
        if data is None:
            raise AssertionError(f"No canned response for {schema.__name__}")
        return schema.model_validate(data)


@pytest.fixture
def fake_llm() -> FakeLLM:
    return FakeLLM()
