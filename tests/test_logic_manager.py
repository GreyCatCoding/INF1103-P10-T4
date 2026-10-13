import pytest
import Logic_Manager

"""Fake ai_manager.analyse_record() outputs, for testing logic_manager without the API.
"""

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

def test_validate_data():
    record = MOCK_RESULTS[0]
    assert Logic_Manager.validate_data(record) is True


def test_get_priority():
    record = MOCK_RESULTS[18]
    assert Logic_Manager.get_priority(record) == "P1"


def test_needs_human_review():
    record = MOCK_RESULTS[18]
    assert Logic_Manager.needs_human_review(record, "P1") is True


def test_get_recommended_action():
    action = Logic_Manager.get_recommended_action("P1", True)
    assert action == "Remove user with human confirmation"


def test_generate_report():
    record = MOCK_RESULTS[18]
    report = Logic_Manager.generate_report(record)
    assert report["priority"] == "P1"


def test_process_reports():
    reports = Logic_Manager.process_reports(MOCK_RESULTS)
    assert len(reports) == 20


def test_get_category_description():
    description = Logic_Manager.get_category_description("spam")
    assert description == "scams, get-rich-quick offers or unsolicited promotion"

def test_evaluate():
    record = MOCK_RESULTS[18]

    decision = Logic_Manager.evaluate(record)

    assert isinstance(decision, dict)
    assert decision["priority"] == "P1"
    assert decision["recommended_action"] == "Remove user with human confirmation"
    assert decision["human_review_required"] is True

def test_route():
    record = MOCK_RESULTS[18]
    
    priority = Logic_Manager.evaluate(record)["priority"]

    action, review_required = Logic_Manager.route(record, priority)

    assert review_required == Logic_Manager.needs_human_review(record, priority)
    assert action == Logic_Manager.get_recommended_action(priority, review_required)

reports = Logic_Manager.process_reports(MOCK_RESULTS) # process all records for logic manager

# Test Result
for report in reports:
    print(report)