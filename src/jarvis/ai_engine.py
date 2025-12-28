"""
JARVIS AI Entegrasyon Motoru

Claude ve OpenAI ile entegrasyonu yönetir.
Aktif uzman prompt'a göre sistem davranışını değiştirir.
"""

from typing import Optional

from anthropic import Anthropic
from openai import OpenAI
from rich.console import Console

from .models import ExpertPrompt, JarvisConfig

console = Console()

# JARVIS Ana Sistem Prompt'u (prompt'tan gelen)
JARVIS_SYSTEM_PROMPT = """
Sen "JARVIS" adlı, sesli konuşabilen ve kullanıcının ekranını görebilen bir yapay zekâ asistansın.

## UZMAN PROMPT KÜTÜPHANESİ MANTIĞI

Uygulamada kullanıcı farklı "Uzman System Prompt"ları kaydedebilir ve istediği an aktif edebilir.
Senin davranışların, her zaman **Aktif Uzman System Prompt**'a göre şekillenir.

### Aktif Prompt Önceliği

* "Aktif Uzman System Prompt" yoksa: **GENEL MOD** ile çalış.
* Aktif prompt varsa: Tüm kararlar ve cevaplar o prompta göre verilir.
* Çelişki olursa öncelik sırası:
  1. Güvenlik + gizlilik
  2. Doğruluk
  3. Kullanıcı hedefi
  4. Aktif Uzman System Prompt
  5. Bu sistem promptunun genel UX kuralları

## EKRAN OKUMA DİSİPLİNİ (HALLÜSİNASYON ÖNLEME)

Her ekrana dayalı yanıtta şu formatı kullan:

**(A) GÖZLEM:** "Ekranda şunları görüyorum: …" (sadece gördüğün)
**(B) AMAÇ:** "Hedefimiz şu mu: …?"
**(C) ÖNERİ:** 1–3 seçenek (en iyi seçeneği öne al)
**(D) ADIMLAR:** 3–7 kısa adım
**(E) KONTROL:** "Şimdi ekranda ne çıktı?"

## SES ODAKLI İLETİŞİM

* Türkçe konuş (kullanıcı aksini istemedikçe).
* Kısa, net, adım adım.
* Tek seferde tek hedef.
* Kritik işlemlerde (silme/ödeme/yayınlama) "geri alınamaz olabilir" uyarısı + onay sor.

## KESİN YASAKLAR

* Gizli bilgi isteme (şifre, OTP, kart, kimlik).
* Görmediğin şeyi gördüm deme.
* Kullanıcı adına işlem yaptığını iddia etme.
* Aktif promptun çizdiği rolün dışına çıkma.
"""


class AIEngine:
    """
    AI Entegrasyon Motoru

    Claude ve OpenAI ile iletişimi yönetir.
    """

    def __init__(self, config: JarvisConfig):
        """
        Args:
            config: JarvisConfig instance
        """
        self.config = config
        self.client = self._init_client()
        self.conversation_history: list[dict] = []

    def _init_client(self):
        """AI client'ı başlat"""
        if self.config.ai_provider == "anthropic":
            if not self.config.anthropic_api_key:
                raise ValueError("ANTHROPIC_API_KEY gerekli!")
            return Anthropic(api_key=self.config.anthropic_api_key)
        elif self.config.ai_provider == "openai":
            if not self.config.openai_api_key:
                raise ValueError("OPENAI_API_KEY gerekli!")
            return OpenAI(api_key=self.config.openai_api_key)
        else:
            raise ValueError(f"Bilinmeyen AI provider: {self.config.ai_provider}")

    def build_system_prompt(
        self, active_prompt: Optional[ExpertPrompt] = None
    ) -> str:
        """
        Sistem prompt'u oluştur

        Args:
            active_prompt: Aktif uzman prompt (None ise GENEL MOD)

        Returns:
            Tam sistem prompt'u
        """
        system_prompt = JARVIS_SYSTEM_PROMPT

        if active_prompt:
            system_prompt += f"""

---
## AKTİF UZMAN SYSTEM PROMPT: {active_prompt.name}

{active_prompt.description or ''}

{active_prompt.prompt_text}
---

ÖNEMLİ: Yukarıdaki uzman prompt'a göre davran. Bu senin şu anki uzmanlık alanın.
"""
        else:
            system_prompt += """

---
## MOD: GENEL MOD

Aktif uzman prompt yok. Genel amaçlı asistan olarak çalış.
Kullanıcıya ekrandaki işlerde destek ol, net adım adım yönlendir.
---
"""

        return system_prompt

    def chat(
        self,
        user_message: str,
        active_prompt: Optional[ExpertPrompt] = None,
        screen_image_base64: Optional[str] = None,
    ) -> str:
        """
        Kullanıcı mesajına cevap ver

        Args:
            user_message: Kullanıcı mesajı
            active_prompt: Aktif uzman prompt
            screen_image_base64: Ekran görüntüsü (base64)

        Returns:
            AI cevabı
        """
        system_prompt = self.build_system_prompt(active_prompt)

        # Mesajı conversation history'e ekle
        message_content = []

        if screen_image_base64:
            # Görsel ekle (Anthropic format)
            if self.config.ai_provider == "anthropic":
                message_content.append(
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": screen_image_base64,
                        },
                    }
                )
            else:
                # OpenAI format (GPT-4 Vision)
                message_content.append(
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{screen_image_base64}"
                        },
                    }
                )

        message_content.append({"type": "text", "text": user_message})

        self.conversation_history.append({"role": "user", "content": message_content})

        try:
            if self.config.ai_provider == "anthropic":
                response = self._chat_anthropic(system_prompt)
            else:
                response = self._chat_openai(system_prompt)

            # AI cevabını history'e ekle
            self.conversation_history.append({"role": "assistant", "content": response})

            return response

        except Exception as e:
            console.print(f"[red]✗ AI hatası: {e}[/red]")
            raise

    def _chat_anthropic(self, system_prompt: str) -> str:
        """Anthropic (Claude) ile konuş"""
        response = self.client.messages.create(
            model=self.config.model_name,
            max_tokens=4096,
            system=system_prompt,
            messages=self.conversation_history,
        )
        return response.content[0].text

    def _chat_openai(self, system_prompt: str) -> str:
        """OpenAI (GPT) ile konuş"""
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(self.conversation_history)

        response = self.client.chat.completions.create(
            model=self.config.model_name, messages=messages, max_tokens=4096
        )
        return response.choices[0].message.content

    def clear_history(self) -> None:
        """Konuşma geçmişini temizle"""
        self.conversation_history = []
        console.print("[green]✓ Konuşma geçmişi temizlendi[/green]")

    def get_conversation_length(self) -> int:
        """Konuşma uzunluğunu al"""
        return len(self.conversation_history)
