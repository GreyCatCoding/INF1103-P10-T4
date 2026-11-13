"""Tries the primary provider first and resorts to fallback provider only if the primary fails."""
import logging

from ai_manager.aiprovider import AIProvider

logger = logging.getLogger(__name__)


class FallbackProvider(AIProvider):
    """AIProvider to wrap two AIProviders."""

    def __init__(self, primary: AIProvider, backup: AIProvider):
        self.__primary = primary
        self.__backup = backup

    def generate(self, system_prompt: str, user_prompt: str) -> str | None:
        """Returns the primary's reply, or the backup's reply if the primary failed."""
        raw_response = self.__primary.generate(system_prompt, user_prompt)
        if raw_response:
            return raw_response

        logger.warning("Main provider failed, falling back to %s", type(self.__backup).__name__)
        return self.__backup.generate(system_prompt, user_prompt)