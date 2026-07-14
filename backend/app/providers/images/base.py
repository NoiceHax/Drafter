"""Image search provider abstraction."""
from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel


class ImageAsset(BaseModel):
    url: str
    thumbnail_url: str | None = None
    source_url: str | None = None
    provider: str
    title: str | None = None
    creator: str | None = None
    license: str | None = None


class ImageSearchProvider(ABC):
    name: str = "base"

    @abstractmethod
    def search_images(self, query: str, *, limit: int = 6) -> list[ImageAsset]:
        """Return discovered image assets for a query."""

    @abstractmethod
    def get_image_metadata(self, identifier: str) -> ImageAsset | None:
        """Return metadata for a single image by provider-specific identifier."""
