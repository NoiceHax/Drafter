"""Prompt for regenerating/refining a single hook."""
from __future__ import annotations

from app.prompts.common import QUALITY_GUARDRAILS


def build(
    *,
    context: str,
    current_hook_text: str,
    archetype: str,
    instruction: str | None,
) -> str:
    extra = (
        f"\nApply this refinement instruction: {instruction}\n"
        if instruction
        else "\nProduce a fresh, stronger variation.\n"
    )
    return f"""You are refining a single video hook.

{QUALITY_GUARDRAILS}

{context}

Current hook: "{current_hook_text}"
Preserve the archetype: {archetype} (do NOT change it unless the instruction explicitly asks).
{extra}
Return ONE hook object with fields: text, archetype, suitability_score (0..1),
estimated_duration_seconds, unanswered_question (or null), story_payoff (or null), reason.
Never invent facts or stakes to make it more dramatic."""
