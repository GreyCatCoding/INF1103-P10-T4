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

def validate_data(data): # Check that the AI output contains valid information

    if not isinstance(data, dict):
        raise ValueError("AI output must be a dictionary")

    required_fields = {
        "harmful", "category", "severity",
        "target", "confidence"
    }

    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing field: {field}")

    if type(data["harmful"]) is not bool:
        raise ValueError("harmful must be True or False")

    if not isinstance(data["category"], str):
        raise ValueError("category must be a string")

    if not isinstance(data["target"], str):
        raise ValueError("target must be a string")

    if type(data["severity"]) is not int:
        raise ValueError("severity must be an integer")

    if not 0 <= data["severity"] <= 4:
        raise ValueError("severity must be between 0 and 4")

    if type(data["confidence"]) not in (int, float):
        raise ValueError("confidence must be numeric")

    if not 0 <= data["confidence"] <= 1:
        raise ValueError("confidence must be between 0 and 1")

    if (
        data["category"].lower() not in CATEGORIES
        and data["category"].lower() != "none"
    ):
        raise ValueError("unknown category")

    return True

def get_priority(data, previous_violations=0):

    validate_data(data)

    # previous_violations is a variable where it identify repeat offenders
    if type(previous_violations) is not int or previous_violations < 0:
        raise ValueError("previous_violations must be non-negative")   

    harmful = data.get("harmful", False)
    category = data.get("category", "none").lower()
    severity = data.get("severity", 0)
    target = data.get("target", "none").lower()
    confidence = data.get("confidence", 0.0)

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
            or previous_violations >= 3
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


def generate_report(data, previous_violations=0):
    
    priority = get_priority(data, previous_violations)

    return {
        "priority": priority,
        "human_review_required": priority in {"P1", "P2"},
    }


Recieved_data = {
    "harmful": True,
    "category": "violence",
    "severity": 4,
    "target": "individual",
    "confidence": 0.95
}


result = generate_report(Recieved_data)

print(result)