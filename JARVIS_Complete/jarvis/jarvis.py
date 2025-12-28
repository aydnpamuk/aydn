"""
JARVIS Ana Uygulama

Tüm modülleri orchestrate eden ana JARVIS sınıfı.
"""

from typing import Optional

from rich.console import Console
from rich.panel import Panel

from .ai_engine import AIEngine
from .config import load_config
from .models import ExpertPrompt, JarvisConfig
from .prompt_library import PromptLibraryManager
from .screen_capture import ScreenCaptureManager
from .voice import VoiceInterface

console = Console()


class JARVIS:
    """
    JARVIS Ana Sınıfı

    Sesli + Ekran destekli AI asistan.
    Tüm modülleri yönetir ve orchestrate eder.
    """

    def __init__(self, config: Optional[JarvisConfig] = None):
        """
        Args:
            config: JarvisConfig instance (None ise otomatik yükle)
        """
        # Konfigürasyon
        self.config = config or load_config()

        # Modülleri başlat
        self.prompt_manager = PromptLibraryManager(self.config.library_path)
        self.screen_capture = ScreenCaptureManager(self.config.screenshots_path)
        self.voice = VoiceInterface(
            language=self.config.voice_language,
            speed=self.config.voice_speed,
            enabled=self.config.voice_enabled,
        )
        self.ai_engine = AIEngine(self.config)

        console.print(
            Panel(
                "[bold cyan]JARVIS[/bold cyan] - Sesli + Ekran Asistan\n"
                f"🤖 AI Provider: {self.config.ai_provider}\n"
                f"🎤 Ses: {'Aktif' if self.config.voice_enabled else 'Devre Dışı'}\n"
                f"📸 Ekran: {'Aktif' if self.config.screen_capture_enabled else 'Devre Dışı'}",
                title="🚀 Başlatılıyor",
                border_style="cyan",
            )
        )

        # Başlangıç mesajı
        self._show_welcome_message()

    def _show_welcome_message(self) -> None:
        """Hoşgeldin mesajı göster"""
        active_prompt = self.prompt_manager.get_active_prompt()

        welcome_msg = "Merhaba! Ben JARVIS. Ekranını görebiliyor ve sesli destek olabiliyorum."

        if active_prompt:
            welcome_msg += f"\n\n🎯 **Aktif Mod:** {active_prompt.name}"
            if active_prompt.description:
                welcome_msg += f"\n📝 {active_prompt.description}"
        else:
            welcome_msg += "\n\n🎯 **Mod:** GENEL MOD (Aktif uzman prompt yok)"

        welcome_msg += "\n\n❓ Şu an hedefimiz ne?"

        console.print(Panel(welcome_msg, border_style="green"))

        # Sesli hoşgeldin (kısa versiyon)
        if self.config.voice_enabled:
            self.voice.speak("Merhaba, ben Jarvis. Size nasıl yardımcı olabilirim?")

    def chat(
        self,
        user_message: str,
        capture_screen: bool = False,
        speak_response: bool = True,
    ) -> str:
        """
        Kullanıcı ile konuş

        Args:
            user_message: Kullanıcı mesajı
            capture_screen: Ekran görüntüsü al
            speak_response: Cevabı sesli söyle

        Returns:
            AI cevabı
        """
        # Aktif prompt'u al
        active_prompt = self.prompt_manager.get_active_prompt()

        # Ekran görüntüsü al (eğer isteniyorsa ve aktifse)
        screen_image_base64 = None
        if capture_screen and self.config.screen_capture_enabled:
            console.print("[cyan]📸 Ekran yakalanıyor...[/cyan]")
            screen_image_base64 = self.screen_capture.capture_to_base64(
                region=self.config.screen_region
            )

        # AI ile konuş
        console.print("[cyan]🤖 Düşünüyorum...[/cyan]")
        response = self.ai_engine.chat(
            user_message=user_message,
            active_prompt=active_prompt,
            screen_image_base64=screen_image_base64,
        )

        # Cevabı göster
        console.print(Panel(response, title="💬 JARVIS", border_style="blue"))

        # Sesli cevap ver
        if speak_response and self.config.voice_enabled:
            # Uzun cevapları kısalt (ses için)
            short_response = self._shorten_for_speech(response)
            self.voice.speak(short_response, play=True)

        return response

    def _shorten_for_speech(self, text: str, max_length: int = 300) -> str:
        """
        Metni ses için kısalt

        Args:
            text: Tam metin
            max_length: Maksimum karakter sayısı

        Returns:
            Kısaltılmış metin
        """
        if len(text) <= max_length:
            return text

        # İlk cümleyi veya paragrafı al
        sentences = text.split(".")
        result = sentences[0] + "."

        if len(result) > max_length:
            result = text[:max_length] + "..."

        return result

    def listen_and_respond(
        self, capture_screen: bool = True, speak_response: bool = True
    ) -> Optional[str]:
        """
        Sesli dinle ve cevap ver

        Args:
            capture_screen: Ekran görüntüsü al
            speak_response: Cevabı sesli söyle

        Returns:
            AI cevabı veya None
        """
        # Kullanıcıyı dinle
        user_message = self.voice.listen(timeout=5, phrase_time_limit=10)

        if not user_message:
            return None

        # Prompt komutlarını kontrol et
        if self._handle_prompt_command(user_message):
            return None

        # Normal sohbet
        return self.chat(
            user_message=user_message,
            capture_screen=capture_screen,
            speak_response=speak_response,
        )

    def _handle_prompt_command(self, user_message: str) -> bool:
        """
        Prompt kütüphanesi komutlarını işle

        Args:
            user_message: Kullanıcı mesajı

        Returns:
            True ise komut işlendi, False ise normal mesaj
        """
        msg_lower = user_message.lower()

        # "Promptları listele"
        if "prompt" in msg_lower and (
            "listele" in msg_lower or "göster" in msg_lower
        ):
            self.prompt_manager.list_prompts(show_table=True)
            if self.config.voice_enabled:
                count = len(self.prompt_manager.library.prompts)
                self.voice.speak(f"{count} adet kayıtlı prompt var.")
            return True

        # "Aktif prompt hangisi"
        if "aktif" in msg_lower and "prompt" in msg_lower:
            active = self.prompt_manager.get_active_prompt()
            if active:
                msg = f"Aktif prompt: {active.name}"
                console.print(f"[green]{msg}[/green]")
                if self.config.voice_enabled:
                    self.voice.speak(msg)
            else:
                msg = "Aktif prompt yok, GENEL MOD aktif."
                console.print(f"[yellow]{msg}[/yellow]")
                if self.config.voice_enabled:
                    self.voice.speak(msg)
            return True

        # "Genel moda dön"
        if "genel mod" in msg_lower and ("dön" in msg_lower or "aktif" in msg_lower):
            self.prompt_manager.set_active(None)
            if self.config.voice_enabled:
                self.voice.speak("Genel mod aktif.")
            return True

        return False

    def interactive_mode(self) -> None:
        """
        İnteraktif mod

        Kullanıcı ile sürekli konuş (text tabanlı).
        """
        console.print(
            Panel(
                "[bold]İnteraktif Mod[/bold]\n"
                "Komutlar:\n"
                "  'çık' - Çıkış\n"
                "  'ekran' - Ekran görüntüsü ile sor\n"
                "  'temizle' - Konuşma geçmişini temizle\n"
                "  'promptlar' - Prompt'ları listele\n"
                "  'aktif' - Aktif prompt'u göster",
                border_style="cyan",
            )
        )

        while True:
            try:
                user_input = console.input("[bold cyan]Sen:[/bold cyan] ").strip()

                if not user_input:
                    continue

                # Çıkış
                if user_input.lower() in ["çık", "exit", "quit"]:
                    console.print("[green]Görüşürüz! 👋[/green]")
                    if self.config.voice_enabled:
                        self.voice.speak("Görüşürüz!")
                    break

                # Ekran ile sor
                if user_input.lower() == "ekran":
                    follow_up = console.input(
                        "[cyan]Ekran hakkında ne sormak istersiniz?[/cyan] "
                    ).strip()
                    if follow_up:
                        self.chat(follow_up, capture_screen=True)
                    continue

                # Konuşma geçmişini temizle
                if user_input.lower() == "temizle":
                    self.ai_engine.clear_history()
                    continue

                # Prompt'ları listele
                if user_input.lower() == "promptlar":
                    self.prompt_manager.list_prompts(show_table=True)
                    continue

                # Aktif prompt
                if user_input.lower() == "aktif":
                    active = self.prompt_manager.get_active_prompt()
                    if active:
                        console.print(f"[green]Aktif: {active.name}[/green]")
                    else:
                        console.print("[yellow]GENEL MOD aktif[/yellow]")
                    continue

                # Normal sohbet
                self.chat(user_input, capture_screen=False, speak_response=True)

            except KeyboardInterrupt:
                console.print("\n[green]Görüşürüz! 👋[/green]")
                break
            except Exception as e:
                console.print(f"[red]Hata: {e}[/red]")

    def voice_mode(self) -> None:
        """
        Sesli mod

        Sürekli dinle ve cevap ver.
        """
        console.print(
            Panel(
                "[bold]Sesli Mod[/bold]\n"
                "Konuşmaya başlayın. (Ctrl+C ile çık)",
                border_style="magenta",
            )
        )

        try:
            while True:
                self.listen_and_respond(capture_screen=True, speak_response=True)
        except KeyboardInterrupt:
            console.print("\n[green]Sesli mod durduruldu.[/green]")
