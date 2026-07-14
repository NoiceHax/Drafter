"""Search provider abstraction for the research pipeline."""
from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel


class SearchResult(BaseModel):
    title: str
    url: str
    publisher: str | None = None
    published_at: str | None = None
    snippet: str = ""
    content: str = ""  # fuller extracted text when available


class SearchProvider(ABC):
    name: str = "base"

    @abstractmethod
    def search(self, query: str, *, max_results: int = 6) -> list[SearchResult]:
        """Return ranked search results for a query."""

    @abstractmethod
    def fetch_content(self, url: str) -> str:
        """Fetch and return the readable text content of a URL (best-effort)."""
