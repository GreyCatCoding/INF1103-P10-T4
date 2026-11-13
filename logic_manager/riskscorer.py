from abc import ABC, abstractmethod

from logic_manager.moderationrecord import ModerationRecord


class RiskScorer(ABC):
    """Any way of turning a ModerationRecord into a 0-100 risk score."""

    @abstractmethod
    def score(self, record: ModerationRecord) -> float:
        """Returns a risk score from 0 to 100."""