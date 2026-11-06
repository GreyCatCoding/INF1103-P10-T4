"""Main provider to call Groq's gpt-oss-safeguard-20b model. The replies are capped at 800 tokens to fit the free tier."""
from chatapiprovider import ChatAPIProvider


class GroqProvider(ChatAPIProvider):
    """Calls Groq's safety-classification model."""

    _BASE_URL = "https://api.groq.com/openai/v1"
    _MODEL = "openai/gpt-oss-safeguard-20b"
    _KEY_ENV = "GROQ_API_KEY"

    __MAX_COMPLETION_TOKENS = 800

    def _extra_body(self) -> dict:
        """Caps the reply length so each request fits Groq's free-tier token limit."""
        return {"max_completion_tokens": self.__MAX_COMPLETION_TOKENS}