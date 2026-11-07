from riskscorer import RiskScorer
from moderationrecord import ModerationRecord
from moderation_policy import ModerationPolicy
from moderation_decision import ModerationDecision

class LogicManager:
    """Coordinates risk scoring and moderation decisions."""

    def __init__(self, scorer: RiskScorer, policy: ModerationPolicy):
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

    
    def create_decision(
        self,
        record: ModerationRecord
    ) -> ModerationDecision:
        """
        Create a complete moderation decision for a valid record.

        Coordinates risk scoring, policy evaluation and routing.
        """

        # Step 1: Calculate the numerical risk score
        risk_score = self.calculate_risk(record)

        # Step 2: Obtain priority, action and human-review status
        policy_result = self.evaluate_policy(record)

        # Step 3: Determine the destination queue
        queue = self.route_record(
            policy_result["human_review_required"]
        )

        # Step 4: Create the ModerationDecision object
        decision = ModerationDecision(
            priority=policy_result["priority"],
            risk_score=risk_score,
            queue=queue,
            recommended_action=policy_result["recommended_action"],
            human_review_required=policy_result["human_review_required"]
        )

        return decision


    def route_record(self, human_review_required: bool) -> str:
        """
        Determine the destination queue based on human review.

        Returns:
            "human_review" if human review is required.
            "standard" otherwise.
        """
        if not isinstance(human_review_required, bool):
            raise ValueError(
                "human_review_required must be a boolean"
            )

        if human_review_required:
            return "human_review"

        return "standard"


    def process_records(self, records: list) -> list:
        """
        Process multiple AI-enriched records.

        Valid records receive complete moderation reports.
        Invalid records are flagged for human review.
        """

        results = []

        for data in records:
            try:
                # Step 1: Validate and create a record object
                record = ModerationRecord(data)

                # Step 2: Generate the full 13-field report
                report = self.generate_report(record)

                # Step 3: Store the completed report
                results.append(report)

            except ValueError as error:
                # Keep processing even if one record is invalid
                results.append({
                    "error": str(error),
                    "human_review_required": True
                })

        return results


    def generate_report(self, record: ModerationRecord) -> dict:
        """
        Generate a complete moderation report.

        Combines the original record information
        with the moderation decision.
        """

        # Create a moderation decision
        decision = self.create_decision(record)

        # Combine record data and decision data
        report = {
            "User ID": record.user_id,
            "username": record.username,
            "comment": record.comment,
            "category": record.category,
            "category_description":
                self._policy.get_category_description(record.category),
            "severity": record.severity,
            "confidence": record.confidence,
            "ai_reason": record.reason,
            **decision.to_dict()
        }

        return report