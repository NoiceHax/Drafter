"""Prompt for refining a creator's rough idea into a clear direction.

The rough input (which may be only a few keywords) is a SEED, not the ground
truth. The model proposes a sharper interpretation, offers alternative
directions, and asks what it needs to know, so the creator can confirm or
steer before the rest of the pipeline builds on it.
"""
from __future__ import annotations

from app.prompts.common import QUALITY_GUARDRAILS

ROLE = (
    "You are a development producer helping a short-form video creator turn a "
    "rough idea into a clear, workable premise. You treat the creator's input "
    "as a starting seed, not a final brief."
)


def build(
    *,
    rough_idea: str,
    platform: str,
    tone: str,
    target_duration_seconds: int,
    instruction: str | None,
    answers: str | None,
) -> str:
    steer = ""
    if answers:
        steer += f"\nThe creator answered your earlier questions with: {answers}\n"
    if instruction:
        steer += f"\nApply this steering instruction: {instruction}\n"

    return f"""{ROLE}

{QUALITY_GUARDRAILS}

The creator gave this rough idea (it may be just a few words; do NOT treat it as
the complete or final intent):
"{rough_idea or '(almost nothing yet)'}"

Format context: platform {platform}, tone {tone}, target ~{target_duration_seconds} seconds.
{steer}
Do the following:
1. refined_idea: Rewrite the rough input as ONE clear, specific premise (1-2
   sentences) that would make a strong video for this format. Make a confident,
   reasonable interpretation; do not just echo the input back.
2. interpretation: In 1-2 sentences, say plainly what you understood the creator
   to mean and what you assumed to fill the gaps, so they can confirm or correct.
3. directions: Offer 3 genuinely different directions the idea could go. For each,
   give a short title and a full one-sentence idea statement. These let the creator
   pick a lane if your main refinement is not what they meant.
4. clarifying_questions: Ask 2-3 specific questions whose answers would most sharpen
   the idea (audience, angle, scope, timeframe, etc.). Keep them short and concrete.

Never invent facts, statistics, or events. It is fine for the premise to be a
question or exploration when the facts are not yet known."""
