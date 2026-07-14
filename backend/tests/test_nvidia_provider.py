"""Tests for NvidiaNIMProvider with a mocked OpenAI-compatible client."""
from __future__ import annotations

from types import SimpleNamespace

import pytest
from pydantic import BaseModel

from app.core.errors import LLMNotConfiguredError, LLMOutputError
from app.providers.llm.base import ChatMessage
from app.providers.llm.nvidia import NvidiaNIMProvider


class Sample(BaseModel):
    name: str
    score: float


def _completion(content: str):
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
    )


class FakeCompletions:
    def __init__(self, contents: list[str]):
        self._contents = contents
        self.calls = 0

    def create(self, **kwargs):
        content = self._contents[min(self.calls, len(self._contents) - 1)]
        self.calls += 1
        return _completion(content)


def _provider_with(contents: list[str]) -> NvidiaNIMProvider:
    p = NvidiaNIMProvider(api_key="test-key", base_url="http://x", model="m")
    p._client = SimpleNamespace(chat=SimpleNamespace(completions=FakeCompletions(contents)))
    return p


def test_requires_api_key():
    with pytest.raises(LLMNotConfiguredError):
        NvidiaNIMProvider(api_key="", base_url="http://x", model="m")


def test_generate_returns_text():
    p = _provider_with(["hello world"])
    out = p.generate([ChatMessage(role="user", content="hi")])
    assert out == "hello world"


def test_structured_parses_valid_json():
    p = _provider_with(['{"name": "a", "score": 0.5}'])
    result = p.generate_structured([ChatMessage(role="user", content="x")], Sample)
    assert result == Sample(name="a", score=0.5)


def test_structured_parses_fenced_json():
    p = _provider_with(['```json\n{"name": "b", "score": 1}\n```'])
    result = p.generate_structured([ChatMessage(role="user", content="x")], Sample)
    assert result.name == "b"


def test_structured_retries_once_then_succeeds():
    # First response is garbage; retry returns valid JSON.
    p = _provider_with(["not json at all", '{"name": "c", "score": 0.9}'])
    result = p.generate_structured([ChatMessage(role="user", content="x")], Sample)
    assert result.name == "c"
    assert p._client.chat.completions.calls == 2


def test_structured_raises_after_failed_retry():
    p = _provider_with(["garbage one", "garbage two"])
    with pytest.raises(LLMOutputError):
        p.generate_structured([ChatMessage(role="user", content="x")], Sample)
