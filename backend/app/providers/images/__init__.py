"""Image search provider factory. Defaults to Wikimedia (no key needed)."""
from __future__ import annotations

from functools import lru_cache

from app.core.config import settings
from app.providers.images.base import ImageAsset, ImageSearchProvider
from app.providers.images.stock import PexelsProvider, UnsplashProvider
from app.providers.images.wikimedia import WikimediaProvider

__all__ = ["ImageAsset", "ImageSearchProvider", "get_image_provider"]


@lru_cache
def get_image_provider() -> ImageSearchProvider:
    provider = settings.image_search_provider.lower()
    if provider == "pexels" and settings.pexels_api_key:
        return PexelsProvider(settings.pexels_api_key)
    if provider == "unsplash" and settings.unsplash_access_key:
        return UnsplashProvider(settings.unsplash_access_key)
    # Wikimedia is always available and requires no key.
    return WikimediaProvider()
