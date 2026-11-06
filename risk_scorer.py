from logic_manager import CATEGORY_WEIGHTS, validate_data

class RiskScorer:
    """Calculate risk scores for the AI-enriched moderation records."""

    def calculate(self, data:dict) -> float:
        """
        Calculate a moderation risk score between 0 and 100
        Higher scores indicate greater assessed risks.
        """

        raise NotImplementedError(
            "Risk score calculation is not implemented yet."
        )
        

    