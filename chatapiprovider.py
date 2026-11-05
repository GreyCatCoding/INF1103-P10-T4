import logging
import os
from abc import abstractmethod

import requests

from aiprovider import AIProvider

logger = logging.getLogger(__name__)


class ChatAPIProvider(AIProvider):
    """Abstract class: sends one chat request to {base_url}/chat/completions."""

    _BASE_URL: str = ""
    _MODEL: str = ""
    _KEY_ENV: str = ""

    def __init__(self, timeout: int = 60):
        """Reads the API key from .env and raises ValueError if it is missing."""
        api_key = os.getenv(self._KEY_ENV)
        # if api_key is missing, raise ValueError
        if not api_key:
            raise ValueError(f"Missing API key: set {self._KEY_ENV} in .env")

        self.__api_key = api_key
        self.__timeout = timeout

    def generate(self, system_prompt: str, user_prompt: str) -> str | None:
        """POST the prompts and returns the model's raw text, or None on failure."""
        api_url = f"{self._BASE_URL}/chat/completions"
        headers = {"Authorization": f"Bearer {self.__api_key}", "Content-Type": "application/json"}
        body = {
            "model": self._MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0,
            "response_format": {"type": "json_object"},
        }
        body.update(self._extra_body()) 

        try:
            # Post a request to the model api
            api_response = requests.post(api_url, headers=headers, json=body, timeout=self.__timeout)
            # Raise an exception if an HTTP request fails
            api_response.raise_for_status()
            # Convert the response JSON into a dict
            response_json = api_response.json()
            # Log which model gave the response
            logger.info("Model used: %s", response_json.get("model"))
            # Extract the model's reply text
            content = response_json["choices"][0]["message"]["content"]
            # Log error in case provider returns None or a list here instead of text
            if not isinstance(content, str):
                logger.error("Model reply is not text: %s", content)
                return None
            return content
        except requests.exceptions.RequestException as err:
            # Covers timeouts, connection errors and HTTP errors
            logger.error("API request failed: %s", err)
        except (ValueError, KeyError, IndexError, TypeError, AttributeError) as err:
            # Covers a reply that isn't JSON, JSON missing "choices"/"message"/"content" or a JSON list where an object was expected
            logger.error("Unexpected API response shape: %s", err)
        # Only reached if one of the excepts above ran
        return None

    @abstractmethod
    def _extra_body(self) -> dict:
        """Extra request fields for specified provider, return {} if none."""