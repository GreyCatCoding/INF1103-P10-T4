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


# ==========================================
# 4. RECOMMENDED ACTION
# ==========================================

def get_recommended_action(priority, review_required):

    if review_required and priority in {"P3", "P4"}:
        return "Send to human moderator for review"

    return ACTIONS[priority]


# ==========================================
# 5. GENERATE REPORT
# ==========================================

def generate_report(data):

    priority = get_priority(data)

    review_required = needs_human_review(
        data, priority
    )

    action = get_recommended_action(
        priority, review_required
    )

    return {
        "User ID": data["User ID"],
        "username": data["username"],
        "comment": data["processed_comments"],
        "category": data["category"],
        "severity": data["severity"],
        "confidence": data["confidence"],
        "priority": priority,
        "recommended_action": action,
        "human_review_required": review_required,
        "ai_reason": data["reason"],
    }


# ==========================================
# 6. PROCESS MULTIPLE RECORDS
# ==========================================

def process_reports(records):

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
                "recommended_action": "Manual review required",
                "human_review_required": True,
                "error": str(error),
            })

    return results


# ==========================================
# 7. TEST WITH MOCK AI RESULTS
# ==========================================

# Trial: Output given by ai_manager
MOCK_RESULTS = [
    {"User ID": 0, "username": "amy", "processed_comments": "great game last night!", "harmful": False, "category": "none", "severity": 0, "target": "none", "confidence": 0.97, "reason": "Positive comment about a game."},
    {"User ID": 1, "username": "ben", "processed_comments": "u r a pathetic l0ser", "harmful": True, "category": "harassment", "severity": 2, "target": "individual", "confidence": 0.93, "reason": "Direct personal insult using disguised spelling."},
    {"User ID": 2, "username": "cal", "processed_comments": "earn $500 a day, DM me now", "harmful": True, "category": "spam", "severity": 1, "target": "none", "confidence": 0.95, "reason": "Unsolicited money-making offer."},
    {"User ID": 3, "username": "dee", "processed_comments": "anyone know when the patch drops?", "harmful": False, "category": "none", "severity": 0, "target": "none", "confidence": 0.98, "reason": "Neutral question."},
    {"User ID": 4, "username": "eli", "processed_comments": "nobody wants you here, just quit already", "harmful": True, "category": "harassment", "severity": 3, "target": "individual", "confidence": 0.88, "reason": "Targeted hostility telling a user to leave."},
    {"User ID": 5, "username": "fay", "processed_comments": "this update is trash lol", "harmful": False, "category": "none", "severity": 0, "target": "none", "confidence": 0.84, "reason": "Criticism of a product, not a person."},
    {"User ID": 6, "username": "gus", "processed_comments": "click here for free skins >>> bit.ly/fr33sk1ns", "harmful": True, "category": "spam", "severity": 2, "target": "none", "confidence": 0.96, "reason": "Suspicious link promising free items."},
    {"User ID": 7, "username": "hana", "processed_comments": "people from that country are all scammers", "harmful": True, "category": "hate", "severity": 3, "target": "group", "confidence": 0.90, "reason": "Negative generalisation about a nationality."},
    {"User ID": 8, "username": "ivan", "processed_comments": "i'm gonna destroy you in the next match", "harmful": False, "category": "none", "severity": 0, "target": "none", "confidence": 0.72, "reason": "Competitive trash talk about a game, not a real threat."},
    {"User ID": 9, "username": "jo", "processed_comments": "ur so dumb it's actually impressive", "harmful": True, "category": "harassment", "severity": 1, "target": "individual", "confidence": 0.61, "reason": "Mild insult; could be playful banter."},
    {"User ID": 10, "username": "kai", "processed_comments": "know where you live. watch yourself.", "harmful": True, "category": "violence", "severity": 4, "target": "individual", "confidence": 0.94, "reason": "Implied threat of violence referencing the user's home."},
    {"User ID": 11, "username": "lea", "processed_comments": "thanks for the help everyone!", "harmful": False, "category": "none", "severity": 0, "target": "none", "confidence": 0.99, "reason": "Friendly thanks."},
    {"User ID": 12, "username": "max", "processed_comments": "buy followers cheap!!! 1000 for $5", "harmful": True, "category": "spam", "severity": 1, "target": "none", "confidence": 0.97, "reason": "Advertising fake followers."},
    {"User ID": 13, "username": "nia", "processed_comments": "go back to where you came from", "harmful": True, "category": "hate", "severity": 3, "target": "group", "confidence": 0.86, "reason": "Exclusionary statement targeting people by origin."},
    {"User ID": 14, "username": "omar", "processed_comments": "that ref was blind, worst call ever", "harmful": False, "category": "none", "severity": 0, "target": "none", "confidence": 0.89, "reason": "Frustration at a decision, no personal attack."},
    {"User ID": 15, "username": "pia", "processed_comments": "lol ok boomer", "harmful": True, "category": "harassment", "severity": 1, "target": "individual", "confidence": 0.55, "reason": "Dismissive remark; borderline."},
    {"User ID": 16, "username": "quinn", "processed_comments": "women can't play this game properly", "harmful": True, "category": "hate", "severity": 2, "target": "group", "confidence": 0.83, "reason": "Demeaning generalisation about women."},
    {"User ID": 17, "username": "ray", "processed_comments": "send me pics of you ;)", "harmful": True, "category": "sexual", "severity": 2, "target": "individual", "confidence": 0.85, "reason": "Unsolicited sexual request aimed at a user."},
    {"User ID": 18, "username": "sam", "processed_comments": "you're the reason this team keeps losing, go hurt yourself", "harmful": True, "category": "self_harm", "severity": 4, "target": "individual", "confidence": 0.91, "reason": "Encourages another user to harm themselves."},
    {"User ID": 19, "username": "tia", "processed_comments": "see you all at the tournament saturday", "harmful": False, "category": "none", "severity": 0, "target": "none", "confidence": 0.98, "reason": "Event reminder."},
]

if __name__ == "__main__":

    reports = process_reports(MOCK_RESULTS)

    for report in reports:

        print("=" * 68)
        print("User ID:", report["User ID"]) 
        print("Username:", report["username"])

        if "error" in report:
            print("Error:", report["error"])
            print("Action:", report["recommended_action"])
        else:
            print("Category:", report["category"])
            print("Priority:", report["priority"])
            print("Action:", report["recommended_action"])
            print("AI Reason:", report["ai_reason"])

        if report["human_review_required"]:
            print("Human Review: Review Required")
        else:
            print("Human Review: Review not Required")

    print("=" * 68)
    print("Total Reports:", len(reports))