"""Tavily search provider."""
from __future__ import annotations

import httpx

from app.core.errors import ProviderError
from app.providers.search.base import SearchProvider, SearchResult


class TavilyProvider(SearchProvider):
    name = "tavily"

    def __init__(self, api_key: str):
        self._api_key = api_key

    def search(self, query: str, *, max_results: int = 6) -> list[SearchResult]:
        try:
            resp = httpx.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": self._api_key,
                    "query": query,
                    "max_results": max_results,
                    "include_answer": False,
                    "search_depth": "advanced",
                },
                timeout=30.0,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            raise ProviderError(f"Tavily search failed: {exc}") from exc

        results: list[SearchResult] = []
        for item in data.get("results", []):
            results.append(
                SearchResult(
                    title=item.get("title") or item.get("url", "Untitled"),
                    url=item.get("url", ""),
                    publisher=None,
                    published_at=item.get("published_date"),
                    snippet=item.get("content", "")[:400],
                    content=item.get("raw_content") or item.get("content", ""),
                )
            )
        return results

    def fetch_content(self, url: str) -> str:
        try:
            resp = httpx.get(url, timeout=20.0, follow_redirects=True)
            resp.raise_for_status()
            return resp.text
        except Exception:
            return ""
