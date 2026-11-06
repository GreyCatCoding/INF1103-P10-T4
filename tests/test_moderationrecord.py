import pytest

from moderationrecord import ModerationRecord

CAL = {"User ID": 2, "username": "cal", "processed_comments": "earn $500 a day, DM me now", "harmful": True, "category": "spam", "severity": 1, "target": "none", "confidence": 0.95, "reason": "Unsolicited money-making offer."}


def test_valid_record_can_be_read():
    record = ModerationRecord(CAL)
    assert (record.username, record.severity, record.confidence) == ("cal", 1, 0.95)


def test_category_is_lowercased():
    record = ModerationRecord({**CAL, "category": "Spam"})
    assert record.category == "spam"


def test_missing_field_raises():
    with pytest.raises(ValueError, match="Missing field: category"):
        ModerationRecord({"User ID": 1})


def test_not_a_dict_raises():
    with pytest.raises(ValueError, match="AI output must be a dictionary"):
        ModerationRecord("hello")


def test_severity_out_of_range_raises():
    with pytest.raises(ValueError, match="severity must be between 0 and 4"):
        ModerationRecord({**CAL, "severity": 7})


def test_fields_are_read_only():
    record = ModerationRecord(CAL)
    with pytest.raises(AttributeError):
        record.severity = 4