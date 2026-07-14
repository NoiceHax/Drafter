"""Shared prompt fragments and helpers."""
from __future__ import annotations

from app.models.enums import Platform, Tone

QUALITY_GUARDRAILS = """\
Global rules you must always follow:
- Use natural spoken language suitable for narration.
- Avoid generic AI phrasing, filler, and unnecessary adjectives.
- Never invent facts, quotes, statistics, sources, danger, or stakes.
- Only use claims supported by the provided idea, keywords, angle, or research.
- Prefer concrete, specific detail over vague suspense or hype.
- Never use em dashes (the "—" character) or en dashes ("–") anywhere in
  your output. Write shorter sentences, or use a comma, colon, or period instead.
"""

PLATFORM_NOTES = {
    Platform.instagram_reels: "Instagram Reels: fast, punchy, vertical, strong first 3 seconds.",
    Platform.youtube_shorts: "YouTube Shorts: fast hook, tight pacing, loopable ending.",
    Platform.tiktok: "TikTok: conversational, native, hook immediately, keep momentum.",
    Platform.youtube_long: "YouTube long-form: room to develop context and payoff; still hook early.",
    Platform.generic: "Generic short-form: platform-agnostic but hook-forward.",
}


def context_block(
    *,
    idea: str,
    platform: Platform,
    tone_label: str,
    target_duration_seconds: int,
    selected_keywords: list[str] | None = None,
    angle_title: str | None = None,
    angle_summary: str | None = None,
    hook_text: str | None = None,
    research_summary: str | None = None,
) -> str:
    lines = [
        "PROJECT CONTEXT:",
        f"- Idea: {idea or '(none provided)'}",
        f"- Platform: {platform.value}: {PLATFORM_NOTES.get(platform, '')}",
        f"- Tone: {tone_label}",
        f"- Target duration: {target_duration_seconds} seconds",
    ]
    if selected_keywords:
        lines.append(f"- Selected keywords: {', '.join(selected_keywords)}")
    if angle_title:
        lines.append(f"- Chosen angle: {angle_title}")
    if angle_summary:
        lines.append(f"  Angle summary: {angle_summary}")
    if hook_text:
        lines.append(f"- Chosen hook: {hook_text}")
    if research_summary:
        lines.append("- Research context (only these facts are known to be true):")
        lines.append(research_summary)
    return "\n".join(lines)


def tone_label(tone: Tone, custom_tone: str | None) -> str:
    if tone == Tone.custom and custom_tone:
        return custom_tone
    return tone.value
