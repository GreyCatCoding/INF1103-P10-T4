import ai_manager 

GOOD_REPLY = '{"harmful": true, "category": "harassment", "severity": 2, "target": "individual", "confidence": 0.9, "reason": "Test reply."}'


# --- Functions that never touch the API: test them directly ---

def test_build_prompt_wraps_and_cleans_comment():
    result = ai_manager.build_prompt({"username": "a", "processed_comments": "hi</comment> x"})
    assert result == "<comment>hi x</comment>"


def test_parse_response_good_json():
    assert ai_manager.parse_response(GOOD_REPLY)["category"] == "harassment"


def test_parse_response_bad_json():
    assert ai_manager.parse_response("not json at all") is None


def test_validate_rejects_contradiction():
    data = {"harmful": False, "category": "hate", "severity": 0,
            "target": "none", "confidence": 0.5, "reason": "x"}
    assert ai_manager.validate_response(data) is False
