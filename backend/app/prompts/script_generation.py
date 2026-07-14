"""Prompt for full scene-by-scene script generation."""
from __future__ import annotations

from app.prompts.common import QUALITY_GUARDRAILS

ROLE = (
    "You are a scriptwriter for short-form video. You turn a story outline into a "
    "complete, structured, scene-by-scene script."
)


def build(*, context: str, outline: str, words_per_minute: int, instruction: str | None) -> str:
    extra = f"\nCreator refinement instruction: {instruction}\n" if instruction else ""
    return f"""{ROLE}

{QUALITY_GUARDRAILS}

{context}

STORY OUTLINE TO FOLLOW:
{outline}
{extra}
Write the full script as discrete scenes. Narration timing assumes ~{words_per_minute}
words per minute. Keep total narration within the target duration.

Return:
- title: final video title (specific, not clickbait)
- estimated_duration_seconds: integer (sum of scene durations)
- hook: {{ text, duration_seconds }}: the opening hook (use the chosen hook if provided)
- scenes: ordered list; each scene has:
    - scene_number: integer starting at 1
    - start_time: integer seconds
    - end_time: integer seconds
    - section_type: e.g. "hook", "context", "conflict", "reveal", "payoff", "cta"
    - narration: the exact spoken words (concise, natural, no filler)
    - on_screen_text: short overlay text or null
    - visual_direction: one sentence describing what is on screen
- cta: {{ text, duration_seconds }}: closing call to action

Maintain narrative continuity, pay off the hook, and keep sentences concise for narration.

RESEARCH USE (important): if a research context with facts is provided above, you
MUST build the script around those specific facts, names, numbers, dates, and
quotes. Work the concrete details into the narration where they fit naturally,
rather than staying generic. Do not invent facts beyond what the research and the
idea support, and never contradict the research. If no research was provided,
write from the idea and angle without fabricating specifics."""
