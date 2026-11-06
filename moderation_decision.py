class ModerationDesicion:
    """Represents the result of a content moderation decison."""

    def __init__(
        self,
        priority: str,
        risk_score: float,
        queue: str,
        recommended_action: str,
        human_review_required: bool
    ):
        self.priority = priority
        self.risk_score = risk_score
        self.queue = queue
        self.recommended_action = recommended_action
        self.human_review_required = human_review_required