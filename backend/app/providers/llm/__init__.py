"""LLM provider factory."""
from __future__ import annotations

from functools import lru_cache

from app.core.config import settings
from app.core.errors import LLMNotConfiguredError
from app.providers.llm.base import ChatMessage, LLMProvider
from app.providers.llm.lazy import LazyLLMProvider
from app.providers.llm.nvidia import NvidiaNIMProvider

__all__ = [
    "ChatMessage",
    "LLMProvider",
    "NvidiaNIMProvider",
    "get_llm_provider",
    "get_lazy_llm_provider",
]


def _build_provider() -> LLMProvider:
    provider = settings.llm_provider.lower()
    if provider == "nvidia":
        return NvidiaNIMProvider(
            api_key=settings.nvidia_api_key,
            base_url=settings.nvidia_base_url,
            model=settings.nvidia_model,
            timeout=settings.nvidia_timeout,
        )
    raise LLMNotConfiguredError(f"Unknown LLM_PROVIDER: {settings.llm_provider!r}")


@lru_cache
def get_llm_provider() -> LLMProvider:
    """Eagerly construct the provider (raises if unconfigured)."""
    return _build_provider()


def get_lazy_llm_provider() -> LLMProvider:
    """Provider that only constructs/validates on first actual use."""
    return LazyLLMProvider(_build_provider)
