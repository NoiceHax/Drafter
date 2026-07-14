"""Post-generation sanitizers applied to all LLM output.

The prompts instruct the model to avoid em/en dashes, but models still slip up,
so this is the enforced safety net: every generated string is cleaned before it
reaches the database or the client.
"""
from __future__ import annotations

from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

# Map dash-like characters to safe replacements.
# Em dash and en dash become ", " (a natural spoken pause); a spaced hyphen
# around them collapses cleanly.
_DASHES = {
    "—": ", ",  # — em dash
    "–": ", ",  # – en dash
    "―": ", ",  # ― horizontal bar
}


def strip_dashes(text: str) -> str:
    if not text:
        return text
    out = text
    for bad, good in _DASHES.items():
        out = out.replace(f" {bad} ", good)  # spaced dash -> ", "
        out = out.replace(bad, good.strip() if good.strip() else "-")
    # Collapse any doubled separators the replacement may create.
    while ", ," in out:
        out = out.replace(", ,", ",")
    return out


def _clean(value):
    if isinstance(value, str):
        return strip_dashes(value)
    if isinstance(value, list):
        return [_clean(v) for v in value]
    if isinstance(value, dict):
        return {k: _clean(v) for k, v in value.items()}
    return value


def strip_dashes_model(model: T) -> T:
    """Return a copy of a Pydantic model with all string fields dash-sanitized."""
    data = _clean(model.model_dump())
    return model.__class__.model_validate(data)
