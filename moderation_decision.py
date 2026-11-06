class ModerationDesicion:
    """Represents the result of a content moderation decison."""

    VALID_PRIORITIES = {"P1", "P2", "P3", "P4"}

    def __init__(
        self,
        priority: str,
        risk_score: float,
        queue: str,
        recommended_action: str,
        human_review_required: bool
    ):
        #Validate Priority
        if priority not in self.VALID_PRIORITIES:
            raise ValueError(
                "Priority must be P1, P2, P3, or P4"
            )

        #Validate Risk Score
        if isinstance(risk_score, bool) or not isinstance(
            risk_score, (int, float)
        ):
            raise TypeError("Risk score must be a number")

        if not 0 <= risk_score <= 100:
            raise ValueError(
                "Risk score must be between 0 and 100"
            )

        #Validate Human Review
        if not isinstance(queue, str) or not queue.strip():
            raise TypeError(
                "Human review required must be a boolen"
            )

        #Validate Text Fields
        if not isinstance(queue, str) or not queue.strip():
            raise ValueError("Queue must be a non-empty string")

        if (
            not isinstance(recommended_action, str)
            or not recommended_action.strip()
        ):
            raise ValueError(
                "Recommended action must be a non-empty string"
            )

        # Store Validated Attributes
        self.priority = priority
        self.risk_score = risk_score
        self.queue = queue
        self.recommended_action = recommended_action
        self.human_review_required = human_review_required

    @property
    def priority(self):
        return self._priority

    @property
    def risk_score(self):
        return self._risk_score

    @property
    def queue(self):
        return self._queue

    @property
    def recommended_action(self):
        return self._recommended_action

    @property
    def human_review_required(self):
        return self._human_review_required