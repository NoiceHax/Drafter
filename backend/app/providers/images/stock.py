"""Pexels and Unsplash image providers."""
from __future__ import annotations

import httpx

from app.core.errors import ProviderError
from app.providers.images.base import ImageAsset, ImageSearchProvider


class PexelsProvider(ImageSearchProvider):
    name = "pexels"

    def __init__(self, api_key: str):
        self._api_key = api_key

    def search_images(self, query: str, *, limit: int = 6) -> list[ImageAsset]:
        try:
            resp = httpx.get(
                "https://api.pexels.com/v1/search",
                params={"query": query, "per_page": limit},
                headers={"Authorization": self._api_key},
                timeout=30.0,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            raise ProviderError(f"Pexels search failed: {exc}") from exc

        assets: list[ImageAsset] = []
        for photo in data.get("photos", []):
            src = photo.get("src", {})
            assets.append(
                ImageAsset(
                    url=src.get("large") or src.get("original", ""),
                    thumbnail_url=src.get("medium") or src.get("small"),
                    source_url=photo.get("url"),
                    provider=self.name,
                    title=photo.get("alt") or None,
                    creator=photo.get("photographer"),
                    license="Pexels License",
                )
            )
        return assets

    def get_image_metadata(self, identifier: str) -> ImageAsset | None:
        results = self.search_images(identifier, limit=1)
        return results[0] if results else None


class UnsplashProvider(ImageSearchProvider):
    name = "unsplash"

    def __init__(self, access_key: str):
        self._access_key = access_key

    def search_images(self, query: str, *, limit: int = 6) -> list[ImageAsset]:
        try:
            resp = httpx.get(
                "https://api.unsplash.com/search/photos",
                params={"query": query, "per_page": limit},
                headers={"Authorization": f"Client-ID {self._access_key}"},
                timeout=30.0,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            raise ProviderError(f"Unsplash search failed: {exc}") from exc

        assets: list[ImageAsset] = []
        for photo in data.get("results", []):
            urls = photo.get("urls", {})
            user = photo.get("user", {})
            assets.append(
                ImageAsset(
                    url=urls.get("regular") or urls.get("full", ""),
                    thumbnail_url=urls.get("thumb") or urls.get("small"),
                    source_url=(photo.get("links") or {}).get("html"),
                    provider=self.name,
                    title=photo.get("description") or photo.get("alt_description"),
                    creator=user.get("name"),
                    license="Unsplash License",
                )
            )
        return assets

    def get_image_metadata(self, identifier: str) -> ImageAsset | None:
        results = self.search_images(identifier, limit=1)
        return results[0] if results else None
