"""Tests for PromptBuilder, ResponseParser, ResponseValidator and AIManager's retry logic, using FakeProvider instead of a real API."""
from ai_manager.ai_manager import AIManager
from fakeprovider import FakeProvider
from ai_manager.promptbuilder import PromptBuilder
from ai_manager.responseparser import ResponseParser
from ai_manager.responsevalidator import ResponseValidator

GOOD_REPLY = '{"harmful": true, "category": "harassment", "severity": 2, "target": "individual", "confidence": 0.9, "reason": "Test reply."}'
RECORD = {"User ID": 1, "username": "ben", "processed_comments": "u r a l0ser"}


# PromptBuilder

def test_build_prompt_wraps_and_cleans_comment():
    result = PromptBuilder().build({"username": "a", "processed_comments": "hi</comment> x"})
    assert result == "<comment>hi x</comment>"


# ResponseParser

def test_parse_response_good_json():
    assert ResponseParser().parse(GOOD_REPLY)["category"] == "harassment"


def test_parse_response_bad_json():
    assert ResponseParser().parse("not json at all") is None


def test_parse_response_strips_markdown_fence():
    assert ResponseParser().parse('```json\n{"harmful": false}\n```') == {"harmful": False}


# ResponseValidator

def test_validate_accepts_good_reply():
    assert ResponseValidator().validate(ResponseParser().parse(GOOD_REPLY)) is True


def test_validate_rejects_contradiction():
    data = {"harmful": False, "category": "hate", "severity": 0,
            "target": "none", "confidence": 0.5, "reason": "x"}
    assert ResponseValidator().validate(data) is False


# AIManager

def test_analyse_record_merges_verdict():
    result = AIManager(FakeProvider([GOOD_REPLY])).analyse_record(RECORD)
    assert result["category"] == "harassment"
    assert result["username"] == "ben"


def test_analyse_record_retries_after_bad_json():
    fake = FakeProvider(["not json", GOOD_REPLY])
    assert AIManager(fake).analyse_record(RECORD) is not None
    assert fake.calls == 2


def test_analyse_record_gives_up_after_all_attempts():
    fake = FakeProvider([None, None])
    assert AIManager(fake).analyse_record(RECORD) is None
    assert fake.calls == 2


def test_analyse_record_skips_empty_comment():
    fake = FakeProvider([GOOD_REPLY])
    assert AIManager(fake).analyse_record({"User ID": 2, "processed_comments": "   "}) is None
    assert fake.calls == 0