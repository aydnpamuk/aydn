"""
Config Testleri
"""

import os

import pytest

from jarvis.config import get_api_key, load_config
from jarvis.models import JarvisConfig


def test_load_config_defaults():
    """Varsayılan config yükleme testi"""
    # Environment değişkenlerini temizle
    env_vars = [
        "JARVIS_AI_PROVIDER",
        "JARVIS_MODEL_NAME",
        "JARVIS_VOICE_ENABLED",
        "JARVIS_DEBUG",
    ]
    original_values = {}
    for var in env_vars:
        original_values[var] = os.environ.get(var)
        if var in os.environ:
            del os.environ[var]

    try:
        config = load_config()

        assert config.ai_provider == "anthropic"
        assert config.voice_enabled is True
        assert config.screen_capture_enabled is True
        assert config.debug_mode is False

    finally:
        # Restore
        for var, value in original_values.items():
            if value is not None:
                os.environ[var] = value


def test_load_config_from_env(monkeypatch):
    """Environment değişkenlerinden config yükleme testi"""
    monkeypatch.setenv("JARVIS_AI_PROVIDER", "openai")
    monkeypatch.setenv("JARVIS_MODEL_NAME", "gpt-4")
    monkeypatch.setenv("JARVIS_VOICE_ENABLED", "false")
    monkeypatch.setenv("JARVIS_DEBUG", "true")

    config = load_config()

    assert config.ai_provider == "openai"
    assert config.model_name == "gpt-4"
    assert config.voice_enabled is False
    assert config.debug_mode is True


def test_get_api_key_anthropic():
    """Anthropic API key getirme testi"""
    config = JarvisConfig(ai_provider="anthropic", anthropic_api_key="test-key-123")

    api_key = get_api_key(config)
    assert api_key == "test-key-123"


def test_get_api_key_openai():
    """OpenAI API key getirme testi"""
    config = JarvisConfig(ai_provider="openai", openai_api_key="test-openai-key")

    api_key = get_api_key(config)
    assert api_key == "test-openai-key"


def test_get_api_key_missing():
    """Eksik API key hatası testi"""
    config = JarvisConfig(ai_provider="anthropic", anthropic_api_key=None)

    with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
        get_api_key(config)


def test_get_api_key_unknown_provider():
    """Bilinmeyen provider hatası testi"""
    config = JarvisConfig(ai_provider="unknown")

    with pytest.raises(ValueError, match="Bilinmeyen AI provider"):
        get_api_key(config)
