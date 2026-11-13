from logic_manager.moderationrecord import ModerationRecord
from logic_manager.riskscorer import RiskScorer


class WeightedRiskScorer(RiskScorer):
    """Risk = 100 x (severity/4) * confidence * category weight, to 1 decimal place."""

    __CATEGORY_WEIGHTS = {"hate": 1.0, "violence": 1.0, "self_harm": 1.0,
                          "harassment": 0.8, "sexual": 0.8, "spam": 0.5, "none": 0.0}

    def score(self, record: ModerationRecord) -> float:
        if not record.harmful:
            return 0.0

        severity_part = record.severity / 4

        weight = self.__CATEGORY_WEIGHTS[record.category]

        risk_score = 100 * severity_part * record.confidence * weight

        return round(risk_score, 1)