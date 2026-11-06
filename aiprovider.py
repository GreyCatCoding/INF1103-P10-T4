"""Takesthe prompts and return the provider model's reply text, or None on failure. All AI providers follows this interface"""
from abc import ABC, abstractmethod


class AIProvider(ABC):
    """Turns a system prompt and a user prompt into the model's raw reply text."""

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> str | None:
        """Returns the model's raw reply text, or None if the call failed."""