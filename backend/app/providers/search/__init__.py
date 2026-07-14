"""Search provider factory. Returns None when research is not configured."""
from __future__ import annotations

from functools import lru_cache

from app.core.config import settings
from app.providers.search.base import SearchProvider, SearchResult
from app.providers.search.other import BraveSearchProvider, SerperProvider
from app.providers.search.tavily import TavilyProvider

__all__ = ["SearchProvider", "SearchResult", "get_search_provider"]


@lru_cache
def get_search_provider() -> SearchProvider | None:
    provider = settings.search_provider.lower()
    if provider == "tavily" and settings.tavily_api_key:
        return TavilyProvider(settings.tavily_api_key)
    if provider == "brave" and settings.brave_search_api_key:
        return BraveSearchProvider(settings.brave_search_api_key)
    if provider == "serper" and settings.serper_api_key:
        return SerperProvider(settings.serper_api_key)
    return None
