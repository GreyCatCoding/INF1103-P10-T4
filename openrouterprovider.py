"""Backup provider to call a free OpenRouter model and gives OpenRouter a list of backup models to try if it is unavailable."""
from chatapiprovider import ChatAPIProvider


class OpenRouterProvider(ChatAPIProvider):
    """Calls OpenRouter to try backup models if the main one is unavailable."""

    _BASE_URL = "https://openrouter.ai/api/v1"
    _MODEL = "nvidia/nemotron-3-super-120b-a12b:free"
    _KEY_ENV = "OPENROUTER_API_KEY"

    # Tried in order if _MODEL is busy
    __BACKUP_MODELS = ["thinkingmachines/inkling-small:free", "openrouter/free"]

    def _extra_body(self) -> dict:
        """Gives OpenRouter its list of backup models."""
        return {"models": self.__BACKUP_MODELS}