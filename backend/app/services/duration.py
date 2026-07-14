"""Narration duration estimation utilities."""
from __future__ import annotations

import re


def count_words(text: str) -> int:
    return len([w for w in re.split(r"\s+", text.strip()) if w])


def estimate_duration_seconds(text: str, words_per_minute: int = 150) -> int:
    """Estimate spoken duration of narration text.

    Uses a configurable words-per-minute rate. Always returns at least 1 second
    for non-empty text.
    """
    if words_per_minute <= 0:
        words_per_minute = 150
    words = count_words(text)
    if words == 0:
        return 0
    seconds = round(words / words_per_minute * 60)
    return max(1, seconds)
