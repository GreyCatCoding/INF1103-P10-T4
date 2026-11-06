
import pytest

from logic_manager_oop import LogicManager
from weightedriskscorer import WeightedRiskScorer
from moderationrecord import ModerationRecord


@pytest.fixture
def manager():
    """Create a LogicManager with a weighted scorer."""
    return LogicManager(WeightedRiskScorer(), None)


@pytest.fixture
def valid_record():
    """Provide a valid AI-enriched comment."""
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


def test_manager_creation(manager):
    """Verify that LogicManager can be instantiated."""
    assert isinstance(manager, LogicManager)


def test_risk_calculation(manager, valid_record):
    """Check that the injected scorer calculates risk."""
    record = ModerationRecord(valid_record)

    assert manager.calculate_risk(record) == 94.0


def test_harmless_content(manager, valid_record):
    """Harmless content should score zero."""
    valid_record["harmful"] = False
    valid_record["severity"] = 0
    valid_record["category"] = "none"

    record = ModerationRecord(valid_record)

    assert manager.calculate_risk(record) == 0.0


def test_batch_processing(manager, valid_record):
    """Process a valid record inside a batch."""
    results = manager.process_records([valid_record])

    assert len(results) == 1
    assert results[0]["username"] == "kai"
    assert results[0]["risk_score"] == 94.0


def test_invalid_record_handling(manager, valid_record):
    """Invalid severity should produce an error result."""
    valid_record["severity"] = 8

    results = manager.process_records([valid_record])

    assert len(results) == 1
    assert results[0]["human_review_required"] is True
    assert "error" in results[0]


def test_batch_continues_after_error(manager, valid_record):
    """An invalid record should not stop the next record."""
    invalid_record = valid_record.copy()
    invalid_record["severity"] = 8

    results = manager.process_records(
        [invalid_record, valid_record]
    )

    assert len(results) == 2
    assert "error" in results[0]
    assert results[1]["risk_score"] == 94.0
