"""NVIDIA NIM LLM provider (OpenAI-compatible API)."""
from __future__ import annotations

import json
from collections.abc import Iterator
from typing import TypeVar

from openai import APIConnectionError, APITimeoutError, OpenAI, RateLimitError
from pydantic import BaseModel, ValidationError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.errors import LLMNotConfiguredError, LLMOutputError, ProviderError
from app.providers.llm.base import ChatMessage, LLMProvider
from app.providers.llm.json_utils import extract_json
from app.providers.llm.sanitize import strip_dashes, strip_dashes_model

T = TypeVar("T", bound=BaseModel)


class NvidiaNIMProvider(LLMProvider):
    """Talks to NVIDIA NIM through its OpenAI-compatible interface."""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        model: str,
        timeout: float = 90.0,
    ):
        if not api_key:
            raise LLMNotConfiguredError(
                "NVIDIA_API_KEY is not configured. Set it in the backend environment."
            )
        self.model = model
        # Explicit per-request timeout so a stalled connection fails fast with a
        # clear error instead of hanging for minutes. We disable the client's
        # own retries because this class implements its own retry policy.
        self._client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=0,
        )

    # ── plain text ────────────────────────────────────────────────────────
    # Retry ONLY transient connection/rate-limit errors, never timeouts (those
    # fail fast so a stalled request doesn't hang for multiples of the timeout).
    @retry(
        retry=retry_if_exception_type((APIConnectionError, RateLimitError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(min=1, max=8),
        reraise=True,
    )
    def _chat(self, messages: list[dict], *, temperature: float, max_tokens: int | None) -> str:
        try:
            resp = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except APITimeoutError as exc:
            raise ProviderError(
                "The model took too long to respond and the request timed out. "
                "Try again, or switch to a faster model (NVIDIA_MODEL)."
            ) from exc
        except (APIConnectionError, RateLimitError):
            raise  # let @retry handle these
        except Exception as exc:  # other API failures
            raise ProviderError(f"NVIDIA NIM request failed: {exc}") from exc
        return resp.choices[0].message.content or ""

    def generate(
        self,
        messages: list[ChatMessage],
        *,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> str:
        payload = [m.model_dump() for m in messages]
        return strip_dashes(self._chat(payload, temperature=temperature, max_tokens=max_tokens))

    # ── structured output ─────────────────────────────────────────────────
    def generate_structured(
        self,
        messages: list[ChatMessage],
        schema: type[T],
        *,
        temperature: float = 0.4,
        max_tokens: int | None = None,
    ) -> T:
        # Cap output so the model can't ramble indefinitely (the main latency
        # driver). Callers may override for larger payloads like full scripts.
        if max_tokens is None:
            max_tokens = 1500
        schema_json = json.dumps(schema.model_json_schema(), indent=2)
        base = [m.model_dump() for m in messages]
        base.append(
            {
                "role": "system",
                "content": (
                    "You must respond with a single valid JSON value that conforms "
                    "exactly to this JSON Schema. Do not include markdown fences, "
                    "comments, or any prose outside the JSON.\n\n"
                    f"JSON Schema:\n{schema_json}"
                ),
            }
        )

        raw = self._chat(base, temperature=temperature, max_tokens=max_tokens)
        parsed = self._try_validate(raw, schema)
        if parsed is not None:
            return strip_dashes_model(parsed)

        # Retry once with an explicit correction instruction.
        correction = base + [
            {"role": "assistant", "content": raw},
            {
                "role": "user",
                "content": (
                    "Your previous response was not valid according to the schema. "
                    "Return ONLY corrected JSON that validates against the schema. "
                    "No prose, no code fences."
                ),
            },
        ]
        raw2 = self._chat(correction, temperature=min(temperature, 0.2), max_tokens=max_tokens)
        parsed = self._try_validate(raw2, schema)
        if parsed is not None:
            return strip_dashes_model(parsed)

        raise LLMOutputError(
            f"Model output failed schema validation for {schema.__name__} after retry."
        )

    @staticmethod
    def _try_validate(raw: str, schema: type[T]) -> T | None:
        try:
            data = extract_json(raw)
        except (json.JSONDecodeError, ValueError):
            return None
        try:
            return schema.model_validate(data)
        except ValidationError:
            return None

    # ── streaming ─────────────────────────────────────────────────────────
    def stream(
        self,
        messages: list[ChatMessage],
        *,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> Iterator[str]:
        payload = [m.model_dump() for m in messages]
        try:
            stream = self._client.chat.completions.create(
                model=self.model,
                messages=payload,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
        except Exception as exc:
            raise ProviderError(f"NVIDIA NIM stream failed: {exc}") from exc
