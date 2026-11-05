from chatapiprovider import ChatAPIProvider


class GroqProvider(ChatAPIProvider):
    """Call Groq model."""

    _BASE_URL = "https://api.groq.com/openai/v1"
    _MODEL = "openai/gpt-oss-safeguard-20b"
    _KEY_ENV = "GROQ_API_KEY"

    def _extra_body(self) -> dict:
        """Groq needs no extra request fields."""
        return {}