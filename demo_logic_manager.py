1
from logic_manager import process_reports

# Three predefined AI outputs
records = [
    {
        "User ID": 1,
        "username": "amy",
        "processed_comments": "Have a great day!",
        "harmful": False,
        "category": "none",
        "severity": 0,
        "target": "none",
        "confidence": 0.97,
        "reason": "No harmful content"
    },
    {
        "User ID": 2,
        "username": "kai",
        "processed_comments": "I will hurt you",
        "harmful": True,
        "category": "violence",
        "severity": 4,
        "target": "individual",
        "confidence": 0.94,
        "reason": "Threat of physical harm"
    },
    {
        "User ID": 3,
        "username": "ben",
        "processed_comments": "You are stupid",
        "harmful": True,
        "category": "harassment",
        "severity": 8,  # Invalid: maximum is 4
        "target": "individual",
        "confidence": 0.90,
        "reason": "Insult"
    }
]

# Process records without calling the AI API
for report in process_reports(records):
    print(f"\nUser: {report['username']}")
    print(f"Priority: {report['priority']}")
    print(f"Risk score: {report['risk_score']}")
    print(f"Action: {report['recommended_action']}")
    print(f"Human review: {report['human_review_required']}")

    if "error" in report:
        print(f"Validation error: {report['error']}")
