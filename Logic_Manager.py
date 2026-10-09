import json


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

ACTIONS = {
    "P1": "Remove user with human confirmation",
    "P2": "Remove content with human confirmation",
    "P3": "Warn user and/or prompt human review",
    "P4": "Monitor user",
}


# ==========================================
# 1. VALIDATE AI OUTPUT
# ==========================================

def validate_data(data): # Check that the AI output contains valid information

    if not isinstance(data, dict):
        raise ValueError("AI output must be a dictionary")

    required_fields = {
        "username",
        "comment",
        "harmful",
        "category",
        "severity",
        "target",
        "confidence",
        "reason",
    }

    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing field: {field}")

    for field in ["username", "comment", "category",
                  "target", "reason"]:
        if not isinstance(data[field], str):
            raise ValueError(f"{field} must be a string")

    if not data["username"].strip():
        raise ValueError("username cannot be empty")

    if not data["comment"].strip():
        raise ValueError("comment cannot be empty")

    if type(data["harmful"]) is not bool:
        raise ValueError("harmful must be boolean")

    if type(data["severity"]) is not int:
        raise ValueError("severity must be an integer")

    if not 0 <= data["severity"] <= 4:
        raise ValueError("severity must be between 0 and 4")

    if type(data["confidence"]) not in (int, float):
        raise ValueError("confidence must be numeric")

    if not 0 <= data["confidence"] <= 1:
        raise ValueError("confidence must be between 0 and 1")

    category = data["category"].lower()

    if category not in CATEGORIES and category != "none":
        raise ValueError("Unknown category")

    if data["target"].lower() not in {
        "individual", "group", "none"
    }:
        raise ValueError("Unknown target")

    return True


# ==========================================
# 2. DETERMINE PRIORITY
# ==========================================

def get_priority(data):

    validate_data(data)

    harmful = data["harmful"]
    category = data["category"].lower()
    severity = data["severity"]
    target = data["target"].lower()
    confidence = data["confidence"]

    # P4: No harmful content detected
    if not harmful or severity == 0:
        return "P4"

    # P1: Severe high-risk harmful content
    if (
        severity == 4
        and confidence >= 0.80
        and (
            category in HIGH_RISK_CATEGORIES
            or target in {"individual", "group"}
        )
    ):
        return "P1"

    # P2: Clearly harmful content
    if severity >= 3 and confidence >= 0.70:
        return "P2"

    # P3: Lower severity harmful content
    return "P3"


# ==========================================
# 3. DETERMINE HUMAN REVIEW
# ==========================================

def needs_human_review(data, priority):

    confidence = data["confidence"]
    severity = data["severity"]

    # Uncertain AI assessment
    if confidence < 0.70:
        return True

    # Severe content
    if severity >= 3:
        return True

    # High-priority moderation
    if priority in {"P1", "P2"}:
        return True

    return False

def generate_report(data):
    
    priority = get_priority(data)

    return {
        "priority": priority,
        "human_review_required": priority in {"P1", "P2"},
        **data
    }

Recieved_data = {
    "harmful": True,
    "category": "violence",
    "severity": 4,
    "target": "individual",
    "confidence": 0.95
}

result = generate_report(Recieved_data)

print(json.dumps(result, indent=4))