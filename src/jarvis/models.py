"""
JARVIS Veri Modelleri

Tüm sistem için kullanılan Pydantic modelleri.
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


class Language(str, Enum):
    """Desteklenen diller"""

    TR = "tr"
    EN = "en"
    TR_EN = "tr+en"


class ExpertPrompt(BaseModel):
    """
    Uzman System Prompt Modeli

    Kullanıcının kaydettiği uzman prompt'ları temsil eder.
    """

    name: str = Field(..., description="Prompt adı (zorunlu)")
    description: Optional[str] = Field(None, description="Promptun açıklaması")
    tags: list[str] = Field(default_factory=list, description="Etiketler")
    language: Language = Field(Language.TR, description="Dil tercihi")
    prompt_text: str = Field(..., description="Asıl system prompt metni")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def update_timestamp(self) -> None:
        """Güncelleme zamanını yenile"""
        self.updated_at = datetime.now()


class PromptLibrary(BaseModel):
    """
    Prompt Kütüphanesi

    Tüm uzman prompt'ları ve aktif prompt'u yönetir.
    """

    prompts: dict[str, ExpertPrompt] = Field(
        default_factory=dict, description="Kayıtlı prompt'lar (name -> ExpertPrompt)"
    )
    active_prompt_name: Optional[str] = Field(
        None, description="Aktif prompt adı (None = GENEL MOD)"
    )

    def add_prompt(self, prompt: ExpertPrompt) -> None:
        """Yeni prompt ekle"""
        self.prompts[prompt.name] = prompt

    def get_prompt(self, name: str) -> Optional[ExpertPrompt]:
        """İsme göre prompt getir"""
        return self.prompts.get(name)

    def delete_prompt(self, name: str) -> bool:
        """Prompt sil"""
        if name in self.prompts:
            del self.prompts[name]
            if self.active_prompt_name == name:
                self.active_prompt_name = None
            return True
        return False

    def set_active(self, name: Optional[str]) -> bool:
        """Aktif prompt'u ayarla (None = GENEL MOD)"""
        if name is None or name in self.prompts:
            self.active_prompt_name = name
            return True
        return False

    def get_active_prompt(self) -> Optional[ExpertPrompt]:
        """Aktif prompt'u getir"""
        if self.active_prompt_name:
            return self.prompts.get(self.active_prompt_name)
        return None

    def list_prompts(self) -> list[str]:
        """Tüm prompt isimlerini listele"""
        return list(self.prompts.keys())


class JarvisConfig(BaseModel):
    """
    JARVIS Konfigürasyonu

    Sistem ayarları ve API anahtarları.
    """

    # AI Provider
    ai_provider: str = Field("anthropic", description="AI sağlayıcı (anthropic/openai)")
    anthropic_api_key: Optional[str] = Field(None, description="Anthropic API key")
    openai_api_key: Optional[str] = Field(None, description="OpenAI API key")
    model_name: str = Field("claude-3-5-sonnet-20241022", description="Model adı")

    # Voice Settings
    voice_enabled: bool = Field(True, description="Ses çıkışı aktif mi?")
    voice_language: str = Field("tr", description="Ses dili")
    voice_speed: float = Field(1.0, description="Konuşma hızı (0.5-2.0)")

    # Screen Capture
    screen_capture_enabled: bool = Field(True, description="Ekran yakalama aktif mi?")
    screen_region: Optional[tuple[int, int, int, int]] = Field(
        None, description="Yakalanacak bölge (x, y, width, height)"
    )

    # Storage
    library_path: Path = Field(
        Path("data/prompt_library.json"), description="Prompt kütüphanesi yolu"
    )
    screenshots_path: Path = Field(
        Path("data/screenshots"), description="Ekran görüntüleri klasörü"
    )

    # System
    debug_mode: bool = Field(False, description="Debug modu")


class ScreenCapture(BaseModel):
    """Ekran görüntüsü modeli"""

    timestamp: datetime = Field(default_factory=datetime.now)
    image_path: Optional[Path] = Field(None, description="Kaydedilmiş görüntü yolu")
    width: int = Field(..., description="Genişlik")
    height: int = Field(..., description="Yükseklik")
    description: Optional[str] = Field(None, description="AI'dan gelen açıklama")


class VoiceMessage(BaseModel):
    """Ses mesajı modeli"""

    text: str = Field(..., description="Mesaj metni")
    language: str = Field("tr", description="Dil")
    timestamp: datetime = Field(default_factory=datetime.now)
    audio_path: Optional[Path] = Field(None, description="Ses dosyası yolu")
