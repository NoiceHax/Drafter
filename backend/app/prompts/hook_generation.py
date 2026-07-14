"""Prompt for narrative hook generation using ten archetypes."""
from __future__ import annotations

from app.prompts.common import QUALITY_GUARDRAILS

ROLE = (
    "You are an expert at writing opening hooks for short-form video. You treat "
    "hooks as narrative opening strategies, not merely different sentence styles."
)

ARCHETYPES = """\
The ten hook archetypes (use these exact keys):
1. mystery_curiosity: Tease a vital piece of information, contradiction, or unexplained
   outcome; withhold the answer to open a specific curiosity gap. NOT vague clickbait.
2. threat: Drop the subject into an escalating crisis/danger/deadline/existential risk.
   Establish who is threatened, what can be lost, and why it is urgent. Stakes must be real.
3. cold_open: Open at a dramatic later moment, then rewind. Must reconnect and pay off.
4. contrarian: Precisely challenge a specific widely-held belief with a real alternative.
   Not "everything you know about X is wrong."
5. problem: Name a specific pain point of the target audience, then promise a path forward.
   Best for tutorials/advice/how-to.
6. statistic: Open on a single striking, real, verifiable number that reframes the topic.
   The number must be supported by the idea or research; never invent figures.
7. story_open: Drop straight into a specific in-the-moment scene or anecdote (a person, a
   place, a concrete action) that pulls the viewer in before any explanation.
8. direct_question: Pose one sharp, specific question the viewer wants answered and that the
   video actually answers. Avoid generic or rhetorical filler questions.
9. comparison: Open on an unexpected juxtaposition of two things (then/now, X vs Y, tiny
   cause vs huge effect) that creates instant intrigue. The contrast must be truthful.
10. pattern_interrupt: Lead with a short, counterintuitive or surprising true statement that
    breaks the viewer's expectation and makes them stop. It must be backed by the story.
"""


def build(*, context: str, instruction: str | None) -> str:
    extra = f"\nCreator refinement instruction: {instruction}\n" if instruction else ""
    return f"""{ROLE}

{QUALITY_GUARDRAILS}

{ARCHETYPES}

{context}
{extra}
Process:
1. Analyze the story's narrative opportunities.
2. For EACH of the ten archetypes, assign a suitability_score (0..1) and a one-sentence
   reason for why it does or does not fit THIS story. Include all ten in "analysis".
3. Generate hooks ONLY for archetypes that genuinely fit (suitability >= ~0.5). Generate
   2-4 hooks total across the strongest archetypes. Never force an archetype to fit.
4. Recommend the single strongest hook via "recommended_index" (0-based index into "hooks").

Each hook must include:
- text: the spoken hook (speakable in ~3-8 seconds for short-form)
- archetype: one of the ten archetype keys
- suitability_score: float 0..1
- estimated_duration_seconds: integer
- unanswered_question: the specific question left in the viewer's mind (or null)
- story_payoff: how/where the script will resolve it (or null)
- reason: one sentence on why this hook works

Hook quality rules: specific not vague; connected to the real story; must be payable off;
natural spoken language; no fake urgency, fabricated stakes, or unsupported claims.
Prefer a concrete curiosity gap ("weeks from disappearing, then one decision changed
everything") over generic suspense ("you won't believe what happened next")."""
