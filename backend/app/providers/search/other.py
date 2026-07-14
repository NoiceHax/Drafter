"""Brave and Serper search providers."""
from __future__ import annotations

import httpx

from app.core.errors import ProviderError
from app.providers.search.base import SearchProvider, SearchResult


class BraveSearchProvider(SearchProvider):
    name = "brave"

    def __init__(self, api_key: str):
        self._api_key = api_key

    def search(self, query: str, *, max_results: int = 6) -> list[SearchResult]:
        try:
            resp = httpx.get(
                "https://api.search.brave.com/res/v1/web/search",
                params={"q": query, "count": max_results},
                headers={"X-Subscription-Token": self._api_key, "Accept": "application/json"},
                timeout=30.0,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            raise ProviderError(f"Brave search failed: {exc}") from exc

        results: list[SearchResult] = []
        for item in data.get("web", {}).get("results", []):
            results.append(
                SearchResult(
                    title=item.get("title", "Untitled"),
                    url=item.get("url", ""),
                    publisher=(item.get("profile") or {}).get("name"),
                    published_at=item.get("age"),
                    snippet=item.get("description", ""),
                    content=item.get("description", ""),
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


class SerperProvider(SearchProvider):
    name = "serper"

    def __init__(self, api_key: str):
        self._api_key = api_key

    def search(self, query: str, *, max_results: int = 6) -> list[SearchResult]:
        try:
            resp = httpx.post(
                "https://google.serper.dev/search",
                json={"q": query, "num": max_results},
                headers={"X-API-KEY": self._api_key, "Content-Type": "application/json"},
                timeout=30.0,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            raise ProviderError(f"Serper search failed: {exc}") from exc

        results: list[SearchResult] = []
        for item in data.get("organic", []):
            results.append(
                SearchResult(
                    title=item.get("title", "Untitled"),
                    url=item.get("link", ""),
                    publisher=item.get("source"),
                    published_at=item.get("date"),
                    snippet=item.get("snippet", ""),
                    content=item.get("snippet", ""),
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
