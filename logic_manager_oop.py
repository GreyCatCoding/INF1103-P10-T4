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
