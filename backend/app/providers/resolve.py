"""Resolve providers using a user's own API keys, falling back to server env.

Per-user keys (stored on the User row) take precedence; when unset, the shared
server-configured keys from settings are used.
"""
from __future__ import annotations

from app.core.config import settings
from app.models.models import User
from app.providers.images import get_image_provider
from app.providers.images.base import ImageSearchProvider
from app.providers.images.stock import PexelsProvider
from app.providers.images.wikimedia import WikimediaProvider
from app.providers.llm.base import LLMProvider
from app.providers.llm.lazy import LazyLLMProvider
from app.providers.llm.nvidia import NvidiaNIMProvider
from app.providers.search import get_search_provider
from app.providers.search.base import SearchProvider
from app.providers.search.tavily import TavilyProvider


def llm_for(user: User | None) -> LLMProvider:
    """Lazy NVIDIA provider using the user's key/model if set, else env."""

    def build() -> LLMProvider:
        api_key = (user.nvidia_api_key if user and user.nvidia_api_key else settings.nvidia_api_key)
        model = (user.nvidia_model if user and user.nvidia_model else settings.nvidia_model)
        return NvidiaNIMProvider(
            api_key=api_key,
            base_url=settings.nvidia_base_url,
            model=model,
            timeout=settings.nvidia_timeout,
        )

    return LazyLLMProvider(build)


def search_for(user: User | None) -> SearchProvider | None:
    """Search provider from the user's Tavily key if set, else env config."""
    if user and user.tavily_api_key:
        return TavilyProvider(user.tavily_api_key)
    return get_search_provider()


def images_for(user: User | None) -> ImageSearchProvider:
    """Image provider from the user's Pexels key if set, else env config."""
    if user and user.pexels_api_key:
        return PexelsProvider(user.pexels_api_key)
    provider = get_image_provider()
    return provider
