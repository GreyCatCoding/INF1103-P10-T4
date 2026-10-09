CATEGORIES = {
    "harassment": "insults, threats or mockery aimed at a specific person",
    "hate": "attacks on a group based on race, religion, nationality, gender, sexuality or disability",
    "violence": "threats, incitement or praise of physical harm",
    "sexual": "explicit sexual content or unwanted sexual comments",
    "self_harm": "encouraging or glorifying suicide or self-injury",
    "spam": "scams, get-rich-quick offers or unsolicited promotion",
}


HIGH_RISK_CATEGORIES = {
    "hate",
    "violence",
    "self_harm"
}

Recieved_data = {
    "harmful": True,
    "category": "violence",
    "severity": 4,
    "target": "individual",
    "confidence": 2
}

def validate_data(Received_data): # Check that the AI output contains valid information

    if not isinstance(Received_data, dict):
        raise ValueError("AI output must be a dictionary")

    required_fields = {
        "harmful", "category", "severity",
        "target", "confidence"
    }

    for field in required_fields:
        if field not in Received_data:
            raise ValueError(f"Missing field: {field}")

    if type(Received_data["harmful"]) is not bool:
        raise ValueError("harmful must be True or False")

    if not isinstance(Received_data["category"], str):
        raise ValueError("category must be a string")

    if not isinstance(Received_data["target"], str):
        raise ValueError("target must be a string")

    if type(Received_data["severity"]) is not int:
        raise ValueError("severity must be an integer")

    if not 0 <= Received_data["severity"] <= 4:
        raise ValueError("severity must be between 0 and 4")

    if type(Received_data["confidence"]) not in (int, float):
        raise ValueError("confidence must be numeric")

    if not 0 <= Received_data["confidence"] <= 1:
        raise ValueError("confidence must be between 0 and 1")

    if (
        Received_data["category"].lower() not in CATEGORIES
        and Received_data["category"].lower() != "none"
    ):
        raise ValueError("unknown category")

    return True

def get_priority(Received_data):

    validate_data(Received_data)

    harmful = Received_data.get("harmful", False)
    category = Received_data.get("category", "none").lower()
    severity = Received_data.get("severity", 0)
    target = Received_data.get("target", "none").lower()
    confidence = Received_data.get("confidence", 0.0)

    # -------------------------
    # P4 - Not harmful / low confidence
    # -------------------------
    if not harmful or severity == 0:
        return "P4"

    # If AI is not confident enough,
    # avoid automatically assigning a high priority
    if confidence < 0.60:
        return "P4"

    # -------------------------
    # P1 - Severe
    # -------------------------
    if (
        severity == 4
        and confidence >= 0.80
        and (
            category in HIGH_RISK_CATEGORIES
            or target in ["individual", "group"]
        )
    ):
        return "P1"

    # -------------------------
    # P2 - Clearly harmful
    # -------------------------
    elif (
        severity >= 3
        and confidence >= 0.70
    ):
        return "P2"

    # -------------------------
    # P3 - Harmful but lower severity
    # -------------------------
    elif (
        severity >= 1
        and harmful
    ):
        return "P3"

    # -------------------------
    # P4 - Default
    # -------------------------
    else:
        return "P4"


print(get_priority(Recieved_data))