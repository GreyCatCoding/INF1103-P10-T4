
import pytest

from logic_manager import score
from risk_scorer import RiskScorer


@pytest.fixture
def scorer():
    """Create a RiskScorer instance for each test."""
    return RiskScorer()


@pytest.fixture
def valid_record():
    """Create a complete, valid AI-enriched record."""
    return {
        "User ID": 2,
        "username": "kai",
        "processed_comments": "I will hurt you",
        "harmful": True,
        "category": "violence",
        "severity": 4,
        "target": "individual",
        "confidence": 0.94,
        "reason": "Threat of physical harm"
    }


def test_risk_scorer_is_object(scorer):
    """Verify that RiskScorer can be instantiated."""
    assert isinstance(scorer, RiskScorer)


def test_severe_harmful_content(scorer, valid_record):
    """A severe violent threat should receive a high score."""
    result = scorer.calculate(valid_record)

    assert result == 94.0


def test_harmless_content(scorer, valid_record):
    """Harmless content should have zero risk."""
    valid_record["harmful"] = False
    valid_record["severity"] = 0
    valid_record["category"] = "none"

    result = scorer.calculate(valid_record)

    assert result == 0.0


def test_invalid_severity(scorer, valid_record):
    """Severity outside the accepted range must be rejected."""
    valid_record["severity"] = 8

    with pytest.raises(ValueError):
        scorer.calculate(valid_record)


def test_invalid_confidence(scorer, valid_record):
    """Confidence greater than 1 must be rejected."""
    valid_record["confidence"] = 1.5

    with pytest.raises(ValueError):
        scorer.calculate(valid_record)


def test_missing_required_field(scorer, valid_record):
    """Missing fields must be rejected by validation."""
    del valid_record["severity"]

    with pytest.raises(ValueError):
        scorer.calculate(valid_record)


@pytest.mark.parametrize(
    "severity,confidence",
    [
        (1, 0.75),
        (2, 0.85),
        (3, 0.90),
        (4, 0.94),
    ],
)
def test_matches_original_score(
    scorer, valid_record, severity, confidence
):
    """OOP scoring must match the original Part 1 function."""
    valid_record["severity"] = severity
    valid_record["confidence"] = confidence

    expected = score(valid_record)
    actual = scorer.calculate(valid_record)

    assert actual == expected
