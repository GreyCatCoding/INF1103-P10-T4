from logic_manager import CATEGORY_WEIGHTS, validate_data

class RiskScorer:
    """Calculate risk scores for the AI-enriched moderation records."""

    def calculate(self, data:dict) -> float:
        """
        Calculate a moderation risk score between 0 and 100
        Higher scores indicate greater assessed risks.
        """

        validate_data(data)

        #If a comment is harmless, its risk score is zero
        if not data["harmful"]:
            return 0.0

        severity_part = data["severity"]/4
        confidence = data["confidence"]
        weight = CATEGORY_WEIGHTS[data["category"].lower()]

        risk_score = 100 * severity_part * confidence * weight

        return round(risk_score, 1)

    