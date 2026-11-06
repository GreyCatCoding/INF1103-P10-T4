class ModerationPolicy:

    CATEGORIES = {
        "harassment": "Insults, threats or mockery aimed at a specific person",
        "hate": (
            "Attacks on a group based on race, religion, nationality, "
            "gender, sexuality or disability"
        ),
        "violence": "Threats, incitement or praise of physical harm",
        "sexual": "Explicit sexual content or unwanted sexual comments",
        "self_harm": "Encouraging or glorifying suicide or self-injury",
        "spam": "Scams, get-rich-quick offers or unsolicited promotion",
        "none": "No harmful content detected",
    }

    HIGH_RISK_CATEGORIES = {"hate", "violence", "self_harm"}

    ACTIONS = {
        "P1": "Remove user with human confirmation",
        "P2": "Remove content with human confirmation",
        "P3": "Warn user and/or prompt human review",
        "P4": "Monitor user",
    }

    #Main functions

    def get_priority(self, data: dict) -> str:
        """Assign a priority based on the moderation assessment."""

        self._validate_policy_data(data)

        harmful = data["harmful"]
        category = data["category"].lower()
        severity = data["severity"]
        target = data["target"].lower()
        confidence = data["confidence"]

        if not harmful or severity == 0:
            return "P4"

        if (
            severity == 4
            and confidence >= 0.80
            and (
                category in self.HIGH_RISK_CATEGORIES
                or target in {"individual", "group"}
            )
        ):
            return "P1"

        if severity >= 3 and confidence >= 0.70:
            return "P2"

        return "P3"

    def needs_human_review(self, data: dict, priority: str) -> bool:
        """Determine whether human review is required."""

        self._validate_policy_data(data)
        self._validate_priority(priority)

        return (
            data["confidence"] < 0.70
            or data["severity"] >= 3
            or priority in {"P1", "P2"}
        )

    def get_recommended_action(
        self,
        priority: str,
        review_required: bool,
    ) -> str:
        """Return the recommended action for a moderation decision."""

        self._validate_priority(priority)

        if type(review_required) is not bool:
            raise ValueError("review_required must be a boolean")

        if review_required and priority in {"P3", "P4"}:
            return "Send to human moderator for review"

        return self.ACTIONS[priority]

    #Extra 

    def _validate_policy_data(self, data: dict) -> None:
        """Check only the fields needed by the moderation policy."""

        if not isinstance(data, dict):
            raise ValueError("Moderation data must be a dictionary")

        required_fields = {
            "harmful", "category", "severity", "target", "confidence"
        }

        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing field: {field}")

        if type(data["harmful"]) is not bool:
            raise ValueError("harmful must be a boolean")

        if not isinstance(data["category"], str):
            raise ValueError("category must be a string")

        if data["category"].lower() not in self.CATEGORIES:
            raise ValueError("Unknown category")

        if type(data["severity"]) is not int:
            raise ValueError("severity must be an integer")

        if not 0 <= data["severity"] <= 4:
            raise ValueError("severity must be between 0 and 4")

        if not isinstance(data["target"], str):
            raise ValueError("target must be a string")

        if data["target"].lower() not in {"individual", "group", "none"}:
            raise ValueError("Unknown target")

        if type(data["confidence"]) not in (int, float):
            raise ValueError("confidence must be numeric")

        if not 0 <= data["confidence"] <= 1:
            raise ValueError("confidence must be between 0 and 1")

    def _validate_priority(self, priority: str) -> None:
        """Check that the supplied priority is supported."""

        if not isinstance(priority, str) or priority not in self.ACTIONS:
            raise ValueError("Priority must be P1, P2, P3 or P4")

    def get_category_description(self, category: str) -> str:
        """Return the description of a supported category."""

        if not isinstance(category, str):
            raise ValueError("category must be a string")

        category = category.lower()

        if category not in self.CATEGORIES:
            raise ValueError("Unknown category")

        return self.CATEGORIES[category]