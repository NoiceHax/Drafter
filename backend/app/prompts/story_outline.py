"""Prompt for generating a structured story outline."""
from __future__ import annotations

from app.prompts.common import QUALITY_GUARDRAILS

ROLE = (
    "You are a story editor for short-form video. You design the narrative structure "
    "of a video before any script is written."
)


def build(*, context: str, instruction: str | None) -> str:
    extra = f"\nCreator refinement instruction: {instruction}\n" if instruction else ""
    return f"""{ROLE}

{QUALITY_GUARDRAILS}

{context}
{extra}
Design a story outline. Choose the narrative structure that best fits THIS topic and
angle. Do NOT force a fixed template. A common (but not mandatory) shape is:
hook -> context -> conflict -> escalation -> reveal -> payoff -> cta.

Return:
- narrative_structure: short label (e.g. "conflict-escalation-reveal")
- estimated_duration_seconds: integer close to the target duration
- sections: ordered list; each section has:
    - type: e.g. "hook", "context", "conflict", "escalation", "reveal", "payoff", "cta"
    - purpose: what this section accomplishes for the viewer
    - summary: the specific content of this section (grounded in known facts)
    - estimated_duration_seconds: integer

Section durations should roughly sum to the target duration. If a chosen hook exists,
the first section must build from it and set up its payoff later in the outline.

If a research context with facts is provided above, ground the section summaries in
those specific facts, names, and numbers so the eventual script can use them. Do not
invent specifics beyond the research and the idea."""
