import pytest

from logic_manager.moderationrecord import ModerationRecord
from logic_manager.riskscorer import RiskScorer
from logic_manager.weightedriskscorer import WeightedRiskScorer

KAI = {"User ID": 10, "username": "kai", "processed_comments": "know where you live. watch yourself.", "harmful": True, "category": "violence", "severity": 4, "target": "individual", "confidence": 0.94, "reason": "Implied threat of violence."}
CAL = {"User ID": 2, "username": "cal", "processed_comments": "earn $500 a day, DM me now", "harmful": True, "category": "spam", "severity": 1, "target": "none", "confidence": 0.95, "reason": "Unsolicited money-making offer."}
AMY = {"User ID": 0, "username": "amy", "processed_comments": "great game last night!", "harmful": False, "category": "none", "severity": 0, "target": "none", "confidence": 0.97, "reason": "Positive comment."}


def test_severe_violence_scores_94():
    assert WeightedRiskScorer().score(ModerationRecord(KAI)) == 94.0


def test_spam_score_rounds_to_one_decimal():
    assert WeightedRiskScorer().score(ModerationRecord(CAL)) == 11.9


def test_not_harmful_scores_zero():
    assert WeightedRiskScorer().score(ModerationRecord(AMY)) == 0.0


def test_weighted_scorer_is_a_risk_scorer():
    assert isinstance(WeightedRiskScorer(), RiskScorer)


def test_abstract_risk_scorer_cannot_be_created():
    with pytest.raises(TypeError):
        RiskScorer()