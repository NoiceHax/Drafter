"""Tests for narration duration estimation."""
from app.services.duration import count_words, estimate_duration_seconds


def test_count_words_handles_whitespace():
    assert count_words("  hello   world  ") == 2
    assert count_words("") == 0


def test_empty_text_is_zero_seconds():
    assert estimate_duration_seconds("", 150) == 0


def test_estimate_scales_with_wpm():
    text = " ".join(["word"] * 150)  # 150 words
    # At 150 wpm, 150 words == 60 seconds.
    assert estimate_duration_seconds(text, 150) == 60
    # At 300 wpm, same text == 30 seconds.
    assert estimate_duration_seconds(text, 300) == 30


def test_short_text_is_at_least_one_second():
    assert estimate_duration_seconds("hi", 150) == 1


def test_invalid_wpm_falls_back_to_default():
    text = " ".join(["word"] * 150)
    assert estimate_duration_seconds(text, 0) == 60
