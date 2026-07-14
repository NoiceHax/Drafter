"""Prompt for content angle generation."""
from __future__ import annotations

from app.prompts.common import QUALITY_GUARDRAILS

ROLE = (
    "You are a content strategist who turns a topic and keywords into distinct, "
    "compelling angles for a short-form video."
)

ANGLE_TYPES = (
    "educational, mystery, conflict, controversial, chronological, investigative, "
    "comparison, rise and fall, hidden history, what nobody tells you, breaking development"
)


def build(*, context: str, instruction: str | None) -> str:
    extra = f"\nCreator refinement instruction: {instruction}\n" if instruction else ""
    return f"""{ROLE}

{QUALITY_GUARDRAILS}

{context}
{extra}
Generate 5 to 8 genuinely distinct content angles. Draw from angle types such as: {ANGLE_TYPES}.
Each angle must include:
- title: a compelling, specific working title (not clickbait, no fabricated numbers)
- summary: 1-2 sentences describing the angle
- style: the angle type (e.g. "investigative", "comparison")
- why_it_works: one concise sentence on the psychological/narrative reason it works
- estimated_audience_interest: float 0..1

Angles must be meaningfully different from each other, not rewordings of one idea."""
