import ai_manager
from promptbuilder import PromptBuilder
from responseparser import ResponseParser

GOOD_REPLY = '{"harmful": true, "category": "harassment", "severity": 2, "target": "individual", "confidence": 0.9, "reason": "Test reply."}'


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


def test_validate_rejects_contradiction():
    data = {"harmful": False, "category": "hate", "severity": 0,
            "target": "none", "confidence": 0.5, "reason": "x"}
    assert ai_manager.validate_response(data) is False