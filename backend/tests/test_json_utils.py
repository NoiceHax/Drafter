"""Tests for lenient JSON extraction from model output."""
import json

import pytest

from app.providers.llm.json_utils import extract_json


def test_plain_json():
    assert extract_json('{"a": 1}') == {"a": 1}


def test_fenced_json():
    text = "Here you go:\n```json\n{\"a\": [1, 2]}\n```\nDone."
    assert extract_json(text) == {"a": [1, 2]}


def test_json_with_leading_prose():
    text = 'Sure! {"keyword": "x", "score": 0.5} hope that helps'
    assert extract_json(text) == {"keyword": "x", "score": 0.5}


def test_array_json():
    assert extract_json("[1, 2, 3]") == [1, 2, 3]


def test_no_json_raises():
    with pytest.raises(json.JSONDecodeError):
        extract_json("there is no json here")
