"""LLM provider abstraction.

Application services depend on `LLMProvider`, never on a concrete client.
This allows future providers (OpenAI, Anthropic, Gemini, local models) to be
added without changing business logic.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class ChatMessage(BaseModel):
    role: str  # "system" | "user" | "assistant"
    content: str


class LLMProvider(ABC):
    """Abstract interface all LLM providers must implement."""

    @abstractmethod
    def generate(
        self,
        messages: list[ChatMessage],
        *,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> str:
        """Return a plain-text completion."""

    @abstractmethod
    def generate_structured(
        self,
        messages: list[ChatMessage],
        schema: type[T],
        *,
        temperature: float = 0.4,
        max_tokens: int | None = None,
    ) -> T:
        """Return a validated instance of `schema`.

        Implementations must attempt to parse JSON, retry once with a
        schema-correction instruction on failure, and raise LLMOutputError
        if validation still fails.
        """

    @abstractmethod
    def stream(
        self,
        messages: list[ChatMessage],
        *,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> Iterator[str]:
        """Yield text chunks as they arrive."""
