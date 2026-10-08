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
    "confidence": 0.95
}

def get_priority(data):

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