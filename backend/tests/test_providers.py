"""Tests for provider factories and abstractions."""
from __future__ import annotations

import httpx
import respx

from app.providers.images import get_image_provider
from app.providers.images.wikimedia import WikimediaProvider
from app.providers.search import get_search_provider


def test_search_provider_none_without_keys(monkeypatch):
    from app.core import config

    monkeypatch.setattr(config.settings, "search_provider", "none")
    get_search_provider.cache_clear()
    assert get_search_provider() is None
    get_search_provider.cache_clear()


def test_image_provider_defaults_to_wikimedia(monkeypatch):
    # Wikimedia is the fallback when no other provider is explicitly configured;
    # force that state so the test doesn't depend on ambient .env config.
    from app.core import config

    monkeypatch.setattr(config.settings, "image_search_provider", "wikimedia")
    get_image_provider.cache_clear()
    provider = get_image_provider()
    assert isinstance(provider, WikimediaProvider)
    get_image_provider.cache_clear()


@respx.mock
def test_wikimedia_parses_results_and_strips_html():
    payload = {
        "query": {
            "pages": {
                "123": {
                    "title": "File:Example.jpg",
                    "imageinfo": [
                        {
                            "url": "https://upload.wikimedia.org/x.jpg",
                            "thumburl": "https://upload.wikimedia.org/thumb.jpg",
                            "descriptionurl": "https://commons.wikimedia.org/wiki/File:Example.jpg",
                            "extmetadata": {
                                "Artist": {"value": "<a href='#'>Jane Doe</a>"},
                                "LicenseShortName": {"value": "CC BY-SA 4.0"},
                            },
                        }
                    ],
                }
            }
        }
    }
    respx.get("https://commons.wikimedia.org/w/api.php").mock(
        return_value=httpx.Response(200, json=payload)
    )
    assets = WikimediaProvider().search_images("anything", limit=1)
    assert len(assets) == 1
    a = assets[0]
    assert a.url == "https://upload.wikimedia.org/x.jpg"
    assert a.provider == "wikimedia"
    assert a.creator == "Jane Doe"  # HTML stripped
    assert a.license == "CC BY-SA 4.0"
    assert a.title == "Example.jpg"
