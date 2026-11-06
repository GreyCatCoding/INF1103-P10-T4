from riskscorer import RiskScorer


class LogicManager:
    """Coordinates risk scoring and moderation decisions."""

    def __init__(self, scorer: RiskScorer, policy):
        """
        Initialise the Logic Manager with its dependencies.

        scorer: An object implementing the RiskScorer interface.
        policy: A moderation policy object.
        """
        self._scorer = scorer
        self._policy = policy
    
    def calculate_risk(self, record) -> float:
        """
        Calculate risk using the injected scoring implementation.

        record: A validated ModerationRecord object.
        """
        return self._scorer.score(record)

    
    def process_records(self, records: list) -> list:
        """
        Validate and calculate risk scores for multiple records.

        Moderation policy integration will be added later.
        """
        from moderationrecord import ModerationRecord

        results = []

        for data in records:
            try:
                record = ModerationRecord(data)
                risk_score = self.calculate_risk(record)

                results.append({
                    "User ID": record.user_id,
                    "username": record.username,
                    "risk_score": risk_score
                })

            except ValueError as error:
                results.append({
                    "error": str(error),
                    "human_review_required": True
                })

        return results

