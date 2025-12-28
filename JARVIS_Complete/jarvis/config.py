"""
JARVIS Konfigürasyon Yöneticisi

.env dosyasından ayarları yükler ve JarvisConfig'i yönetir.
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from .models import JarvisConfig

# .env dosyasını yükle
load_dotenv()


def load_config(config_path: Optional[Path] = None) -> JarvisConfig:
    """
    Konfigürasyonu yükle

    Öncelik sırası:
    1. Environment variables
    2. .env dosyası
    3. Varsayılan değerler

    Args:
        config_path: Özel config dosyası yolu (opsiyonel)

    Returns:
        JarvisConfig instance
    """
    config_data = {
        "ai_provider": os.getenv("JARVIS_AI_PROVIDER", "anthropic"),
        "anthropic_api_key": os.getenv("ANTHROPIC_API_KEY"),
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "model_name": os.getenv(
            "JARVIS_MODEL_NAME", "claude-3-5-sonnet-20241022"
        ),
        "voice_enabled": os.getenv("JARVIS_VOICE_ENABLED", "true").lower() == "true",
        "voice_language": os.getenv("JARVIS_VOICE_LANGUAGE", "tr"),
        "voice_speed": float(os.getenv("JARVIS_VOICE_SPEED", "1.0")),
        "screen_capture_enabled": os.getenv("JARVIS_SCREEN_ENABLED", "true").lower()
        == "true",
        "library_path": Path(
            os.getenv("JARVIS_LIBRARY_PATH", "data/prompt_library.json")
        ),
        "screenshots_path": Path(
            os.getenv("JARVIS_SCREENSHOTS_PATH", "data/screenshots")
        ),
        "debug_mode": os.getenv("JARVIS_DEBUG", "false").lower() == "true",
    }

    config = JarvisConfig(**config_data)

    # Gerekli klasörleri oluştur
    config.library_path.parent.mkdir(parents=True, exist_ok=True)
    config.screenshots_path.mkdir(parents=True, exist_ok=True)

    return config


def get_api_key(config: JarvisConfig) -> str:
    """
    Aktif AI provider için API key'i getir

    Args:
        config: JarvisConfig instance

    Returns:
        API key

    Raises:
        ValueError: API key bulunamazsa
    """
    if config.ai_provider == "anthropic":
        if not config.anthropic_api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable bulunamadı! "
                ".env dosyasına ekleyin veya export edin."
            )
        return config.anthropic_api_key
    elif config.ai_provider == "openai":
        if not config.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable bulunamadı! "
                ".env dosyasına ekleyin veya export edin."
            )
        return config.openai_api_key
    else:
        raise ValueError(f"Bilinmeyen AI provider: {config.ai_provider}")
