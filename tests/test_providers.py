"""Tests for the providers, FallbackProvider and ProviderFactory."""
from unittest.mock import Mock

import pytest
import requests

from fakeprovider import FakeProvider
from ai_manager.fallbackprovider import FallbackProvider
from ai_manager.groqprovider import GroqProvider
from ai_manager.openrouterprovider import OpenRouterProvider
from ai_manager.providerfactory import ProviderFactory

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


def test_groq_sends_no_backup_models(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    sent = {}
    monkeypatch.setattr(requests, "post", fake_post(sent))
    GroqProvider().generate("rules", "<comment>hi</comment>")
    assert "models" not in sent


def test_openrouter_sends_backup_models(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    sent = {}
    monkeypatch.setattr(requests, "post", fake_post(sent))
    OpenRouterProvider().generate("rules", "<comment>hi</comment>")
    assert sent["models"] == ["thinkingmachines/inkling-small:free", "openrouter/free"]



def test_fallback_uses_backup_when_primary_fails():
    provider = FallbackProvider(FakeProvider([None]), FakeProvider(["backup reply"]))
    assert provider.generate("rules", "<comment>hi</comment>") == "backup reply"


def test_fallback_skips_backup_when_primary_works():
    backup = FakeProvider(["backup reply"])
    provider = FallbackProvider(FakeProvider(["main reply"]), backup)
    assert provider.generate("rules", "<comment>hi</comment>") == "main reply"
    assert backup.calls == 0



def test_factory_wraps_groq_with_openrouter_backup(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "groq")
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    assert isinstance(ProviderFactory.from_env(), FallbackProvider)


def test_factory_uses_groq_alone_without_backup_key(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "groq")
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    assert isinstance(ProviderFactory.from_env(), GroqProvider)


def test_factory_rejects_unknown_provider(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "gemini")
    with pytest.raises(ValueError):
        ProviderFactory.from_env()

def test_http_error_logs_provider_message(monkeypatch, caplog):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    response = Mock()
    response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "413 Client Error", response=Mock(text="Request too large: TPM Limit 2000"))
    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: response)
    assert GroqProvider().generate("rules", "<comment>hi</comment>") is None
    assert "TPM Limit 2000" in caplog.text

def test_groq_caps_reply_length(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    sent = {}
    monkeypatch.setattr(requests, "post", fake_post(sent))
    GroqProvider().generate("rules", "<comment>hi</comment>")
    assert sent["max_completion_tokens"] == 800