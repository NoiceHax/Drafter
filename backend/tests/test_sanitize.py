"""Tests for the em/en-dash sanitizer applied to all LLM output."""
from pydantic import BaseModel

from app.providers.llm.sanitize import strip_dashes, strip_dashes_model


def test_strips_spaced_em_dash():
    assert strip_dashes("weeks away — then it changed") == "weeks away, then it changed"


def test_strips_unspaced_em_dash():
    assert "—" not in strip_dashes("a—b")


def test_strips_en_dash():
    assert "–" not in strip_dashes("2020–2024 was pivotal")


def test_leaves_plain_text_untouched():
    assert strip_dashes("plain sentence, with a comma.") == "plain sentence, with a comma."


def test_no_double_separators():
    out = strip_dashes("one — two — three")
    assert ", ," not in out
    assert "—" not in out


class _Sample(BaseModel):
    title: str
    items: list[str]
    nested: dict


def test_strip_dashes_model_recurses():
    m = _Sample(
        title="A — B",
        items=["x — y", "clean"],
        nested={"k": "p — q"},
    )
    cleaned = strip_dashes_model(m)
    assert "—" not in cleaned.title
    assert all("—" not in i for i in cleaned.items)
    assert "—" not in cleaned.nested["k"]
