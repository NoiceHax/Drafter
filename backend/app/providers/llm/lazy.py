"""A lazy LLM provider that defers construction until first use.

This lets services that don't call the LLM (e.g. selecting a keyword) be
constructed even when no API key is configured. The controlled
LLMNotConfiguredError is only raised if the model is actually invoked.
"""
from __future__ import annotations

from collections.abc import Iterator
from typing import Callable, TypeVar

from pydantic import BaseModel

from app.providers.llm.base import ChatMessage, LLMProvider

T = TypeVar("T", bound=BaseModel)


class LazyLLMProvider(LLMProvider):
    def __init__(self, factory: Callable[[], LLMProvider]):
        self._factory = factory
        self._inner: LLMProvider | None = None

    def _get(self) -> LLMProvider:
        if self._inner is None:
            self._inner = self._factory()
        return self._inner

    def generate(self, messages, *, temperature=0.7, max_tokens=None) -> str:
        return self._get().generate(messages, temperature=temperature, max_tokens=max_tokens)

    def generate_structured(self, messages, schema: type[T], *, temperature=0.4, max_tokens=None) -> T:
        return self._get().generate_structured(
            messages, schema, temperature=temperature, max_tokens=max_tokens
        )

    def stream(self, messages, *, temperature=0.7, max_tokens=None) -> Iterator[str]:
        return self._get().stream(messages, temperature=temperature, max_tokens=max_tokens)
