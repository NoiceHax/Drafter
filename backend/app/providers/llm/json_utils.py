"""Helpers for coercing LLM text into valid JSON."""
from __future__ import annotations

import json
import re
from typing import Any


def extract_json(text: str) -> Any:
    """Best-effort extraction of a JSON object/array from model output.

    Handles fenced code blocks, leading prose, and trailing commentary.
    Raises json.JSONDecodeError if nothing parseable is found.
    """
    text = text.strip()

    # Strip ```json ... ``` or ``` ... ``` fences.
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if fence:
        text = fence.group(1).strip()

    # Fast path.
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Fallback: grab the outermost {...} or [...] span.
    start_candidates = [i for i in (text.find("{"), text.find("[")) if i != -1]
    if not start_candidates:
        raise json.JSONDecodeError("No JSON found", text, 0)
    start = min(start_candidates)
    opener = text[start]
    closer = "}" if opener == "{" else "]"
    end = text.rfind(closer)
    if end == -1 or end < start:
        raise json.JSONDecodeError("Unbalanced JSON", text, start)
    return json.loads(text[start : end + 1])
