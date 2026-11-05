from unittest.mock import Mock

import pytest
import requests

from groqprovider import GroqProvider

API_REPLY = {"model": "test-model", "choices": [{"message": {"content": "hello"}}]}


def fake_post(sent: dict):
    """Returns makeshift requests.post that saves the request body into sent."""
    def post(url, headers, json, timeout):
        sent.update(json)
        response = Mock()
        response.json.return_value = API_REPLY
        return response
    return post


def test_missing_api_key_raises(monkeypatch):   
    monkeypatch.delenv("GROQ_API_KEY", raising=False)  # test when .env has no Groq key
    with pytest.raises(ValueError):
        GroqProvider()


def test_generate_returns_model_text(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.setattr(requests, "post", fake_post({}))
    assert GroqProvider().generate("rules", "<comment>hi</comment>") == API_REPLY['choices'][0]['message']['content']


def test_generate_returns_none_when_api_unreachable(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")

    def no_internet(*args, **kwargs):
        raise requests.exceptions.ConnectionError("no internet")

    monkeypatch.setattr(requests, "post", no_internet)
    assert GroqProvider().generate("rules", "<comment>hi</comment>") is None