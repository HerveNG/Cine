import pytest
from fastapi import HTTPException

from app.core.config import Settings
from app.services.ai.factory import get_ai_provider
from app.services.ai.local_provider import LocalProvider


def _patch_settings(monkeypatch, **overrides):
    base = dict(AI_PROVIDER="none", AI_API_KEY="", AI_MODEL="")
    base.update(overrides)
    monkeypatch.setattr("app.services.ai.factory.settings", Settings(**base))


def test_local_provider_selected(monkeypatch):
    _patch_settings(monkeypatch, AI_PROVIDER="local")
    assert isinstance(get_ai_provider(), LocalProvider)


def test_none_provider_raises_503(monkeypatch):
    _patch_settings(monkeypatch, AI_PROVIDER="none")
    with pytest.raises(HTTPException) as exc_info:
        get_ai_provider()
    assert exc_info.value.status_code == 503


def test_anthropic_without_key_raises_503(monkeypatch):
    _patch_settings(monkeypatch, AI_PROVIDER="anthropic", AI_API_KEY="")
    with pytest.raises(HTTPException) as exc_info:
        get_ai_provider()
    assert exc_info.value.status_code == 503


def test_anthropic_with_key_selected(monkeypatch):
    _patch_settings(monkeypatch, AI_PROVIDER="anthropic", AI_API_KEY="sk-ant-fake", AI_MODEL="claude-sonnet-5")
    from app.services.ai.anthropic_provider import AnthropicProvider

    assert isinstance(get_ai_provider(), AnthropicProvider)


def test_openai_without_key_raises_503(monkeypatch):
    _patch_settings(monkeypatch, AI_PROVIDER="openai", AI_API_KEY="")
    with pytest.raises(HTTPException) as exc_info:
        get_ai_provider()
    assert exc_info.value.status_code == 503


def test_openai_with_key_selected(monkeypatch):
    _patch_settings(monkeypatch, AI_PROVIDER="openai", AI_API_KEY="sk-fake", AI_MODEL="gpt-5")
    from app.services.ai.openai_provider import OpenAIProvider

    assert isinstance(get_ai_provider(), OpenAIProvider)
