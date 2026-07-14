"""Prompt for regenerating a single scene's narration and/or visual direction."""
from __future__ import annotations

from app.prompts.common import QUALITY_GUARDRAILS


def build(
    *,
    context: str,
    scene_json: str,
    field: str,
    words_per_minute: int,
    instruction: str | None,
) -> str:
    extra = f"\nRefinement instruction: {instruction}\n" if instruction else ""
    if field == "narration":
        target = "Rewrite ONLY the narration. Keep it within the scene's time window."
    elif field == "visual_direction":
        target = "Rewrite ONLY the visual_direction. Keep narration unchanged."
    else:
        target = "You may rewrite narration, on_screen_text, and visual_direction."

    return f"""You are refining a single scene of an existing video script.
Regenerate only this scene; do not alter the rest of the script.

{QUALITY_GUARDRAILS}

{context}

CURRENT SCENE:
{scene_json}

{target}
Narration timing assumes ~{words_per_minute} words per minute; respect the scene duration.
{extra}
Return the full scene object with fields: scene_number, start_time, end_time,
section_type, narration, on_screen_text (or null), visual_direction (or null).
Keep scene_number, start_time, and end_time the same unless the instruction requires change."""
