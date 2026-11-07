from riskscorer import RiskScorer
from moderationrecord import ModerationRecord
from moderation_policy import ModerationPolicy

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

    def evaluate_policy(self, record: ModerationRecord) -> dict:
        """
        Evaluate moderation priority and action using
        the injected ModerationPolicy.
        """

        # Convert object properties into the dictionary
        # expected by ModerationPolicy.
        policy_data = {
            "harmful": record.harmful,
            "category": record.category,
            "severity": record.severity,
            "target": record.target,
            "confidence": record.confidence
        }

        priority = self._policy.get_priority(policy_data)

        review_required = self._policy.needs_human_review(
            policy_data,
            priority
        )

        action = self._policy.get_recommended_action(
            priority,
            review_required
        )

        return {
            "priority": priority,
            "recommended_action": action,
            "human_review_required": review_required
        }
    
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

