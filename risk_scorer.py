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

        #NotImplementedError still being raise as the numerical calculation hasn't been added yet.
        raise NotImplementedError(
            "Risk score calculation is not implemented yet."
        )
        

    