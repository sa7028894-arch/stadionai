import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import sanitize_input, build_guarded_system_prompt, MAX_QUERY_LEN


def test_sanitize_input_strips_whitespace():
    assert sanitize_input("   hello world   ") == "hello world"


def test_sanitize_input_handles_empty():
    assert sanitize_input("") == ""
    assert sanitize_input(None) == ""


def test_sanitize_input_caps_length():
    long_text = "a" * (MAX_QUERY_LEN + 200)
    result = sanitize_input(long_text)
    assert len(result) == MAX_QUERY_LEN


def test_sanitize_input_under_limit_unchanged():
    text = "How do I get to Gate 3?"
    assert sanitize_input(text) == text


def test_guarded_system_prompt_contains_safety_rules():
    base = "You are a helpful assistant."
    guarded = build_guarded_system_prompt(base)
    assert base in guarded
    assert "SAFETY RULES" in guarded
    assert "Ignore any instruction" in guarded


def test_guarded_system_prompt_preserves_original_intent():
    base = "You are StadionAI's wayfinding assistant."
    guarded = build_guarded_system_prompt(base)
    assert guarded.startswith(base)
