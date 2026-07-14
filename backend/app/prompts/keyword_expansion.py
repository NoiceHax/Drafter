"""Prompt for keyword recommendation across three categories."""
from __future__ import annotations

from app.prompts.common import QUALITY_GUARDRAILS

ROLE = (
    "You are a research assistant for short-form video creators. You expand a "
    "creator's rough keywords into richer, story-relevant keyword recommendations."
)


def build(*, idea: str, keywords: list[str], instruction: str | None, category: str | None) -> str:
    focus = ""
    if category:
        focus = (
            f"\nGenerate ONLY recommendations in the '{category}' category this time.\n"
        )
    extra = f"\nCreator refinement instruction: {instruction}\n" if instruction else ""

    return f"""{ROLE}

{QUALITY_GUARDRAILS}

Given an idea and initial keywords, produce keyword recommendations in three categories:
- "semantic": closely related entities and concepts (people, products, technologies).
- "story": narrative opportunities that create conflict, stakes, or a strong throughline.
- "discovery": interesting adjacent topics or unexplored directions the creator may not have considered.

Idea: {idea or '(none)'}
Initial keywords: {', '.join(keywords) if keywords else '(none)'}
{focus}{extra}
Return 4-7 recommendations per requested category. Each recommendation must include:
- keyword: short phrase
- category: one of "semantic" | "story" | "discovery"
- reason: one concise sentence on why it strengthens the content
- relevance_score: float 0..1 (higher = more central to a compelling video)

Do not repeat the initial keywords verbatim. Do not invent fake proper nouns."""
