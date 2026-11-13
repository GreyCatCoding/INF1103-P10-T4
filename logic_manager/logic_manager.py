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

CATEGORY_WEIGHTS = {
    "hate": 1.0,
    "violence": 1.0,
    "self_harm": 1.0,
    "harassment": 0.8,
    "sexual": 0.8,
    "spam": 0.5,
    "none": 0.0,
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

def validate_data(data: dict) -> None:

    if not isinstance(data, dict):
        raise ValueError("AI output must be a dictionary")

    required_fields = {
        "User ID",
        "username",
        "processed_comments",
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

    for field in ["username", "processed_comments", "category",
                  "target", "reason"]:
        if not isinstance(data[field], str):
            raise ValueError(f"{field} must be a string")

    if type(data["User ID"]) is not int or data["User ID"] < 0:
        raise ValueError("User ID must be a non-negative integer")

    if not data["username"].strip():
        raise ValueError("username cannot be empty")

    if not data["processed_comments"].strip():
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

def get_priority(data: dict) -> str:

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

def evaluate(data: dict) -> dict:    # Validate AI output and determine moderation priority

    priority = get_priority(data)

    # Determine whether human review is required
    review_required = needs_human_review(data, priority)

    # Determine recommended moderation action
    action = get_recommended_action(priority, review_required)

    # Return the moderation decision as a dictionary
    return {
        "priority": priority,
        "recommended_action": action,
        "human_review_required": review_required
    }

def score(data: dict) -> float:
    """
    Calculate a numeric risk score from 0 to 100.
    Higher scores indicate greater assessed moderation risk.
    """

    validate_data(data)

    if not data["harmful"]:
        return 0.0

    severity_part = data["severity"] / 4
    confidence = data["confidence"]
    weight = CATEGORY_WEIGHTS[data["category"].lower()]

    risk_score = 100 * severity_part * confidence * weight

    return round(risk_score, 1)


# ==========================================
# 3. DETERMINE HUMAN REVIEW
# ==========================================

def needs_human_review(data: dict, priority: str) -> bool:

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


# ==========================================
# 4. RECOMMENDED ACTION
# ==========================================

def get_recommended_action(priority: str, review_required: bool) -> str:

    if review_required and priority in {"P3", "P4"}:
        return "Send to human moderator for review"

    return ACTIONS[priority]

def route(record: dict) -> dict:
    """
    Determine the moderation route for a record.
    Returns its priority, destination queue, and recommended action.
    """

    decision = evaluate(record)

    if decision["human_review_required"]:
        queue = "human_review"
    else:
        queue = "standard"

    return {
        "priority": decision["priority"],
        "queue": queue,
        "recommended_action": decision["recommended_action"],
        "human_review_required": decision["human_review_required"],
    }


# ==========================================
# 5. GENERATE REPORT
# ==========================================

def generate_report(data: dict) -> dict:

    decision = evaluate(data)

    priority = decision["priority"]
    action = decision["recommended_action"]
    review_required = decision["human_review_required"]

    routing = route(data)

    return {
        "User ID": data["User ID"],
        "username": data["username"],
        "comment": data["processed_comments"],
        "category": data["category"],
        "category_description": get_category_description(data["category"]),
        "severity": data["severity"],
        "confidence": data["confidence"],
        "risk_score": score(data),
        "priority": priority,
        "queue": routing["queue"],
        "recommended_action": action,
        "human_review_required": review_required,
        "ai_reason": data["reason"],
    }


# ==========================================
# 6. PROCESS MULTIPLE RECORDS
# ==========================================

def process_reports(records: list) -> list:

    results = []

    for record in records:
        try:
            result = generate_report(record)
            results.append(result)

        except ValueError as error:
            results.append({
                "User ID": record.get("User ID", "unknown")
                    if isinstance(record, dict) else "unknown",
                "username": record.get("username", "unknown")
                    if isinstance(record, dict) else "unknown",
                "priority": None,
                "risk_score": None,
                "recommended_action": "Manual review required",
                "human_review_required": True,
                "error": str(error),
            })

    results.sort(
        key=lambda r: r["risk_score"] if r["risk_score"] is not None else 101,
        reverse=True
    )

    return results


# ==========================================
# 7. CATEGORIES DICTIONARY
# ==========================================

def get_category_description(category: str) -> str:
    
    category = category.lower()

    if category == "none":
        return "No harmful content detected"

    elif category in CATEGORIES:
        return CATEGORIES[category]

    else:
        raise ValueError("Unknown category")