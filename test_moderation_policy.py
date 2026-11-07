from ModerationPolicy import ModerationPolicy

import logging

policy = ModerationPolicy()

# Each test contains:
# name, input data, expected priority, expected review, expected action
test_cases = [
    (
        "Severe violence",
        {
            "harmful": True,
            "category": "violence",
            "severity": 4,
            "target": "individual",
            "confidence": 0.90,
        },
        "P1",
        True,
        "Remove user with human confirmation",
    ),
    (
        "High-severity harassment",
        {
            "harmful": True,
            "category": "harassment",
            "severity": 3,
            "target": "individual",
            "confidence": 0.85,
        },
        "P2",
        True,
        "Remove content with human confirmation",
    ),
    (
        "Lower-severity spam",
        {
            "harmful": True,
            "category": "spam",
            "severity": 1,
            "target": "none",
            "confidence": 0.90,
        },
        "P3",
        False,
        "Warn user and/or prompt human review",
    ),
    (
        "Uncertain harmful content",
        {
            "harmful": True,
            "category": "harassment",
            "severity": 2,
            "target": "individual",
            "confidence": 0.50,
        },
        "P3",
        True,
        "Send to human moderator for review",
    ),
    (
        "Harmless content",
        {
            "harmful": False,
            "category": "none",
            "severity": 0,
            "target": "none",
            "confidence": 0.95,
        },
        "P4",
        False,
        "Monitor user",
    ),
    (
        "Uncertain harmless assessment",
        {
            "harmful": False,
            "category": "none",
            "severity": 0,
            "target": "none",
            "confidence": 0.40,
        },
        "P4",
        True,
        "Send to human moderator for review",
    ),
]


def test_decisions():
    for name, data, expected_priority, expected_review, expected_action in test_cases:
        priority = policy.get_priority(data)
        review = policy.needs_human_review(data, priority)
        action = policy.get_recommended_action(priority, review)

        assert priority == expected_priority, (
            f"{name}: expected {expected_priority}, got {priority}"
        )
        assert review == expected_review, (
            f"{name}: expected review={expected_review}, got {review}"
        )
        assert action == expected_action, (
            f"{name}: expected action '{expected_action}', got '{action}'"
        )

        logging.info(f"PASS: {name} | {priority} | Human review: {review}")


def test_category_description():
    description = policy.get_category_description("none")

    assert description == "No harmful content detected"
    logging.info("PASS: Category description")


def test_invalid_data():
    # Copy a valid record, then deliberately make confidence invalid.
    invalid_data = test_cases[0][1].copy()
    invalid_data["confidence"] = 1.50

    try:
        policy.get_priority(invalid_data)
    except ValueError as error:
        logging.info(f"PASS: Invalid confidence rejected | {error}")
    else:
        raise AssertionError("Invalid confidence was accepted")


if __name__ == "__main__":
    test_decisions()
    test_category_description()
    test_invalid_data()

    logging.info("\nAll 8 tests passed!")