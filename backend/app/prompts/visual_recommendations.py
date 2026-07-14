"""Prompt for per-scene visual recommendations and search queries."""
from __future__ import annotations

from app.prompts.common import QUALITY_GUARDRAILS

ROLE = (
    "You are a visual producer for short-form video. For a given scene you recommend "
    "specific visuals and the exact search queries needed to find them."
)

VISUAL_TYPES = (
    "real_image, historical_photo, person, event, location, product, news_headline, "
    "map, chart, screenshot, b_roll, generated_image, text_animation"
)


def build(*, context: str, scene_json: str, instruction: str | None) -> str:
    extra = f"\nRefinement instruction: {instruction}\n" if instruction else ""
    return f"""{ROLE}

{QUALITY_GUARDRAILS}

{context}

SCENE:
{scene_json}
{extra}
Recommend 2-4 visuals for this scene. Decide the right TYPE for each (one of:
{VISUAL_TYPES}). Choose based on what the narration needs, e.g. a real photograph, archival
image, headline, b-roll, map, chart, generated illustration, or text-only animation.

Each recommendation must include:
- type: one of the visual types above
- query: a HIGHLY SPECIFIC search query (e.g. "Jensen Huang holding NVIDIA Blackwell B200
  GPU GTC 2024 keynote", NOT "NVIDIA image")
- description: what the visual should show and how to use it
- reason: why this visual serves the scene
- priority: "high" | "medium" | "low"

These are RECOMMENDATIONS, not discovered images. Never claim an image already exists."""
