
import pytest

from logic_manager.moderation_decision import ModerationDecision


@pytest.fixture
def valid_decision():
    """Create a valid moderation decision for testing."""
    return {
        "priority": "P1",
        "risk_score": 94.0,
        "queue": "human_review",
        "recommended_action": "Remove user with human confirmation",
        "human_review_required": True
    }


def test_valid_decision(valid_decision):
    """A valid decision should be created successfully."""
    decision = ModerationDecision(**valid_decision)

    assert decision.priority == "P1"
    assert decision.risk_score == 94.0
    assert decision.queue == "human_review"
    assert decision.human_review_required is True


def test_invalid_priority(valid_decision):
    """An unsupported priority should be rejected."""
    valid_decision["priority"] = "P9"

    with pytest.raises(ValueError):
        ModerationDecision(**valid_decision)


def test_invalid_risk_score(valid_decision):
    """Risk scores above 100 should be rejected."""
    valid_decision["risk_score"] = 150.0

    with pytest.raises(ValueError):
        ModerationDecision(**valid_decision)


def test_invalid_risk_type(valid_decision):
    """Risk scores must be numeric, not strings."""
    valid_decision["risk_score"] = "high"

    with pytest.raises(TypeError):
        ModerationDecision(**valid_decision)


def test_invalid_human_review(valid_decision):
    """Human-review status must be a boolean."""
    valid_decision["human_review_required"] = "True"

    with pytest.raises(TypeError):
        ModerationDecision(**valid_decision)


def test_empty_queue(valid_decision):
    """An empty queue should be rejected."""
    valid_decision["queue"] = ""

    with pytest.raises(ValueError):
        ModerationDecision(**valid_decision)


def test_empty_action(valid_decision):
    """An empty recommended action should be rejected."""
    valid_decision["recommended_action"] = "   "

    with pytest.raises(ValueError):
        ModerationDecision(**valid_decision)


def test_read_only_property(valid_decision):
    """Priority cannot be changed through its property."""
    decision = ModerationDecision(**valid_decision)

    with pytest.raises(AttributeError):
        decision.priority = "P2"


def test_to_dict(valid_decision):
    """Decision should export all five fields correctly."""
    decision = ModerationDecision(**valid_decision)

    assert decision.to_dict() == valid_decision
