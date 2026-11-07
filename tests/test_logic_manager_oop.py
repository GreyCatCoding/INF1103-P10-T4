import pytest

from logic_manager_oop import LogicManager
from weightedriskscorer import WeightedRiskScorer
from moderationrecord import ModerationRecord
from moderation_policy import ModerationPolicy


@pytest.fixture
def manager():
    return LogicManager(
        scorer=WeightedRiskScorer(),
        policy=ModerationPolicy()
    )


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


def test_batch_sorted_by_risk(manager, valid_record):
    """
    Valid reports should be sorted by descending risk score.
    """

    # Create three independent copies of the valid record.
    low_risk = valid_record.copy()
    medium_risk = valid_record.copy()
    high_risk = valid_record.copy()

    # Change severity while retaining valid record fields.
    low_risk["severity"] = 1
    medium_risk["severity"] = 2
    high_risk["severity"] = 4

    # Give each record a different identity.
    low_risk["User ID"] = 101
    medium_risk["User ID"] = 102
    high_risk["User ID"] = 103

    # Intentionally provide records in the wrong order.
    reports = manager.process_records([
        low_risk,
        high_risk,
        medium_risk
    ])

    scores = [report["risk_score"] for report in reports]

    assert scores == sorted(scores, reverse=True)
    assert [report["User ID"] for report in reports] == [
        103, 102, 101
    ]


def test_invalid_records_appear_first(manager, valid_record):
    """
    Invalid records must appear before valid moderation reports.
    """

    # Create two valid records.
    low_risk = valid_record.copy()
    low_risk["User ID"] = 101
    low_risk["severity"] = 1

    high_risk = valid_record.copy()
    high_risk["User ID"] = 102
    high_risk["severity"] = 4

    # Create an invalid record.
    invalid_record = valid_record.copy()
    invalid_record["User ID"] = 103
    invalid_record["severity"] = 8

    # Intentionally place the invalid record last.
    reports = manager.process_records([
        low_risk,
        high_risk,
        invalid_record
    ])

    # The invalid record should appear first.
    assert "error" in reports[0]
    assert reports[0]["human_review_required"] is True

    # Valid reports should follow in descending risk order.
    assert reports[1]["User ID"] == 102
    assert reports[2]["User ID"] == 101

    assert reports[1]["risk_score"] >= reports[2]["risk_score"]