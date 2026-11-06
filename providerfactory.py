"""Builds the right AIProvider from the AI_PROVIDER setting in .env."""
import logging
import os

from aiprovider import AIProvider
from fallbackprovider import FallbackProvider
from groqprovider import GroqProvider
from openrouterprovider import OpenRouterProvider

logger = logging.getLogger(__name__)


class ProviderFactory:
    """Reads .env once at startup and returns a ready-to-use AIProvider."""

    __REGISTRY = {"groq": GroqProvider, "openrouter": OpenRouterProvider}
    __DEFAULT = "groq"
    __FALLBACK = "openrouter"

    @classmethod
    def from_env(cls) -> AIProvider:
        """Returns the provider named in AI_PROVIDER, wrapped with a backup if one is available.

        Raises ValueError if AI_PROVIDER is unknown or the main provider's API key is missing.
        """
        name = os.getenv("AI_PROVIDER", cls.__DEFAULT)

        if name not in cls.__REGISTRY:
            raise ValueError(f"Unknown AI_PROVIDER: {name}")

        primary = cls.__REGISTRY[name]()  # Builds provider and raises ValueError if the key is missing

        if name == cls.__FALLBACK:
            return primary

        try:
            backup = cls.__REGISTRY[cls.__FALLBACK]()
        except ValueError as err:
            logger.warning("No fallback provider: %s", err)
            return primary

        return FallbackProvider(primary, backup)