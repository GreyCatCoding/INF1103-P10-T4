class ModerationPolicy:
    """Assign moderation priorities, human review and recommended actions.

    Expects a dictionary that has already passed validate_data().
    """

    CATEGORIES = {
        "harassment": "insults, threats or mockery aimed at a specific person",
        "hate": (
            "attacks on a group based on race, religion, nationality, "
            "gender, sexuality or disability"
        ),
        "violence": "threats, incitement or praise of physical harm",
        "sexual": "explicit sexual content or unwanted sexual comments",
        "self_harm": "encouraging or glorifying suicide or self-injury",
        "spam": "scams, get-rich-quick offers or unsolicited promotion",
    }

    HIGH_RISK_CATEGORIES = {
        "hate",
        "violence",
        "self_harm",
    }

    ACTIONS = {
        "P1": "Remove user with human confirmation",
        "P2": "Remove content with human confirmation",
        "P3": "Warn user and/or prompt human review",
        "P4": "Monitor user",
    }

    def get_priority(self, data: dict) -> str:
        """Determine the priority of a validated moderation record."""

        harmful = data["harmful"]
        category = data["category"].lower()
        severity = data["severity"]
        target = data["target"].lower()
        confidence = data["confidence"]

        # P4: No harmful content detected.
        if not harmful or severity == 0:
            return "P4"

        # P1: Severe content with sufficiently high confidence.
        if (
            severity == 4
            and confidence >= 0.80
            and (
                category in self.HIGH_RISK_CATEGORIES
                or target in {"individual", "group"}
            )
        ):
            return "P1"

        # P2: Clearly harmful content.
        if severity >= 3 and confidence >= 0.70:
            return "P2"

        # P3: Other harmful content.
        return "P3"

    def needs_human_review(self, data: dict, priority: str) -> bool:
        """Determine whether a human moderator must review the record."""

        if priority not in self.ACTIONS:
            raise ValueError("Priority must be P1, P2, P3 or P4")

        # Uncertain AI assessment.
        if data["confidence"] < 0.70:
            return True

        # Severe content.
        if data["severity"] >= 3:
            return True

        # Actions requiring human confirmation.
        if priority in {"P1", "P2"}:
            return True

        return False

    def get_recommended_action(
        self,
        priority: str,
        review_required: bool,
    ) -> str:
        """Return an action recommendation without carrying it out."""

        if priority not in self.ACTIONS:
            raise ValueError("Priority must be P1, P2, P3 or P4")

        if review_required and priority in {"P3", "P4"}:
            return "Send to human moderator for review"

        return self.ACTIONS[priority]

    def get_category_description(self, category: str) -> str:
        """Return a readable explanation of the moderation category."""

        category = category.lower()

        if category == "none":
            return "No harmful content detected"

        if category in self.CATEGORIES:
            return self.CATEGORIES[category]

        raise ValueError("Unknown category")

    