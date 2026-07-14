"""Wikimedia Commons image provider (free, no API key required)."""
from __future__ import annotations

import re

import httpx

from app.core.errors import ProviderError
from app.providers.images.base import ImageAsset, ImageSearchProvider

# Filler words to drop when simplifying an over-specific query.
_STOPWORDS = {
    "a", "an", "the", "of", "on", "in", "and", "or", "with", "to", "for", "into",
    "clean", "bold", "close-up", "closeup", "high-contrast", "high", "contrast",
    "photo", "photograph", "image", "picture", "clip", "clipping", "footage",
    "b-roll", "broll", "shot", "screenshot", "title", "card", "background",
    "effect", "vertical", "video", "scene", "showing", "should", "text",
}

_API = "https://commons.wikimedia.org/w/api.php"
# Wikimedia requires a descriptive User-Agent with contact info, else returns 403.
_HEADERS = {
    "User-Agent": (
        "AIContentCopilot/1.0 (https://github.com/ai-content-copilot; "
        "contact: creator@local) httpx"
    ),
    "Accept": "application/json",
}


class WikimediaProvider(ImageSearchProvider):
    name = "wikimedia"

    def search_images(self, query: str, *, limit: int = 6) -> list[ImageAsset]:
        """Search Commons, progressively simplifying an over-specific query.

        LLM-generated queries are optimized for Google-style image search and are
        often far too specific for Commons (which has a smaller, differently
        indexed corpus). We try the full query first, then increasingly broad
        variants, returning the first non-empty result set so a scene still gets
        real assets instead of nothing.
        """
        for variant in _query_variants(query):
            assets = self._search_once(variant, limit=limit)
            if assets:
                return assets
        return []

    def _search_once(self, query: str, *, limit: int = 6) -> list[ImageAsset]:
        if not query.strip():
            return []
        try:
            search = httpx.get(
                _API,
                params={
                    "action": "query",
                    "format": "json",
                    "generator": "search",
                    "gsrsearch": f"filetype:bitmap {query}",
                    "gsrnamespace": 6,  # File namespace
                    "gsrlimit": limit,
                    "prop": "imageinfo",
                    "iiprop": "url|extmetadata|thumburl",
                    "iiurlwidth": 400,
                },
                headers=_HEADERS,
                timeout=30.0,
            )
            search.raise_for_status()
            data = search.json()
        except Exception as exc:
            raise ProviderError(f"Wikimedia search failed: {exc}") from exc

        pages = (data.get("query") or {}).get("pages") or {}
        assets: list[ImageAsset] = []
        for page in pages.values():
            info = (page.get("imageinfo") or [{}])[0]
            meta = info.get("extmetadata") or {}
            assets.append(
                ImageAsset(
                    url=info.get("url", ""),
                    thumbnail_url=info.get("thumburl") or info.get("url"),
                    source_url=info.get("descriptionurl"),
                    provider=self.name,
                    title=page.get("title", "").replace("File:", ""),
                    creator=_clean(meta.get("Artist", {}).get("value")),
                    license=_clean(meta.get("LicenseShortName", {}).get("value")),
                )
            )
        return [a for a in assets if a.url]

    def get_image_metadata(self, identifier: str) -> ImageAsset | None:
        results = self.search_images(identifier, limit=1)
        return results[0] if results else None


def _clean(value: str | None) -> str | None:
    if not value:
        return None
    # extmetadata values can contain HTML; strip tags crudely.
    return re.sub(r"<[^>]+>", "", value).strip() or None


def _query_variants(query: str) -> list[str]:
    """Yield progressively broader search variants for an over-specific query.

    Order (most specific first): original → punctuation stripped →
    content words only → first 4 content words → first 2 content words.
    Duplicates and empties are removed while preserving order.
    """
    variants: list[str] = []

    def add(v: str) -> None:
        v = re.sub(r"\s+", " ", v).strip()
        if v and v.lower() not in {x.lower() for x in variants}:
            variants.append(v)

    original = query.strip()
    add(original)

    # Strip quotes/punctuation.
    depunct = re.sub(r"[\"'“”‘’(),.:;\-–—/]", " ", original)
    add(depunct)

    # Content words only (drop stopwords + pure numbers-as-noise kept if useful).
    words = [w for w in depunct.split() if w]
    content = [w for w in words if w.lower() not in _STOPWORDS]
    add(" ".join(content))

    # First few content words (capture the salient nouns/entities).
    if len(content) > 4:
        add(" ".join(content[:4]))
    if len(content) > 2:
        add(" ".join(content[:2]))

    return variants
