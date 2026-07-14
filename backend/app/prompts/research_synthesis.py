"""Prompt for synthesizing raw search results into structured research sources."""
from __future__ import annotations

from app.prompts.common import QUALITY_GUARDRAILS

ROLE = (
    "You are a fact-checking research analyst. You synthesize raw search results into "
    "concise, source-attributed research notes for a video script."
)


def build(*, context: str, raw_results: str) -> str:
    return f"""{ROLE}

{QUALITY_GUARDRAILS}

CRITICAL: You must NOT invent sources. Only use the search results provided below.
For each source you keep, extract the relevant summary and concrete key facts.
Do not attribute a fact to a source that does not support it.

{context}

RAW SEARCH RESULTS (the only sources you may use):
{raw_results}

Return a list of sources. Each source must include:
- title: source title
- url: source URL (must be one of the URLs above)
- publisher: publisher name or null
- published_at: ISO date string or null
- summary: relevant extracted information (2-4 sentences)
- key_facts: list of concrete, verifiable facts drawn from this source

Only include sources that contain information relevant to the idea/angle. Drop irrelevant ones."""
