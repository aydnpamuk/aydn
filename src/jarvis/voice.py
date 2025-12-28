"""
JARVIS Ses Arayüzü

Text-to-Speech (TTS) ve Speech-to-Text (STT) işlemlerini yönetir.
"""

import os
import tempfile
from pathlib import Path
from typing import Optional

import speech_recognition as sr
from gtts import gTTS
from rich.console import Console

from .models import VoiceMessage

console = Console()


class VoiceInterface:
    """
    Ses Arayüzü

    TTS ve STT işlemlerini yönetir.
    """

    def __init__(
        self,
        language: str = "tr",
        speed: float = 1.0,
        enabled: bool = True,
    ):
        """
        Args:
            language: Dil kodu (tr, en, vb.)
            speed: Konuşma hızı (0.5-2.0, şu an gTTS desteklemiyor)
            enabled: Ses çıkışı aktif mi?
        """
        self.language = language
        self.speed = speed
        self.enabled = enabled
        self.recognizer = sr.Recognizer()

    def speak(
        self, text: str, save_path: Optional[Path] = None, play: bool = True
    ) -> VoiceMessage:
        """
        Metni sese çevir ve çal

        Args:
            text: Konuşulacak metin
            save_path: Ses dosyasını kaydetmek için yol (opsiyonel)
            play: True ise sesi çal

        Returns:
            VoiceMessage model
        """
        if not self.enabled:
            console.print("[yellow]⚠ Ses çıkışı devre dışı[/yellow]")
            return VoiceMessage(text=text, language=self.language)

        try:
            # gTTS ile ses oluştur
            tts = gTTS(text=text, lang=self.language, slow=False)

            # Ses dosyasını kaydet
            if save_path:
                audio_path = save_path
            else:
                # Geçici dosya oluştur
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                audio_path = Path(temp_file.name)

            tts.save(str(audio_path))

            # Sesi çal (platform bağımlı)
            if play:
                self._play_audio(audio_path)

            voice_msg = VoiceMessage(
                text=text, language=self.language, audio_path=audio_path
            )

            console.print(f"[green]🔊 Konuşuyor: {text[:50]}...[/green]")
            return voice_msg

        except Exception as e:
            console.print(f"[red]✗ TTS hatası: {e}[/red]")
            raise

    def _play_audio(self, audio_path: Path) -> None:
        """
        Ses dosyasını çal (platform bağımlı)

        Args:
            audio_path: Çalınacak ses dosyası yolu
        """
        try:
            # Linux
            if os.name == "posix":
                import subprocess

                # mpg123 veya ffplay kullanmayı dene
                try:
                    subprocess.run(
                        ["mpg123", "-q", str(audio_path)],
                        check=True,
                        stderr=subprocess.DEVNULL,
                    )
                except FileNotFoundError:
                    try:
                        subprocess.run(
                            ["ffplay", "-nodisp", "-autoexit", str(audio_path)],
                            check=True,
                            stderr=subprocess.DEVNULL,
                        )
                    except FileNotFoundError:
                        console.print(
                            "[yellow]⚠ mpg123 veya ffplay bulunamadı. Ses çalınamıyor.[/yellow]"
                        )
            # macOS
            elif os.name == "darwin":
                os.system(f'afplay "{audio_path}"')
            # Windows
            elif os.name == "nt":
                os.system(f'start /min "" "{audio_path}"')

        except Exception as e:
            console.print(f"[yellow]⚠ Ses çalma hatası: {e}[/yellow]")

    def listen(
        self, timeout: int = 5, phrase_time_limit: int = 10
    ) -> Optional[str]:
        """
        Mikrofon ile ses dinle ve metne çevir

        Args:
            timeout: Dinleme timeout süresi (saniye)
            phrase_time_limit: Maksimum konuşma süresi (saniye)

        Returns:
            Tanınan metin veya None
        """
        if not self.enabled:
            console.print("[yellow]⚠ Ses girişi devre dışı[/yellow]")
            return None

        try:
            with sr.Microphone() as source:
                console.print("[cyan]🎤 Dinliyorum...[/cyan]")

                # Ortam gürültüsünü ayarla
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

                # Dinle
                audio = self.recognizer.listen(
                    source, timeout=timeout, phrase_time_limit=phrase_time_limit
                )

                console.print("[cyan]🔍 Tanınıyor...[/cyan]")

                # Google Speech Recognition ile tanı
                text = self.recognizer.recognize_google(audio, language=self.language)
                console.print(f"[green]✓ Tanındı: {text}[/green]")
                return text

        except sr.WaitTimeoutError:
            console.print("[yellow]⚠ Dinleme zaman aşımı[/yellow]")
            return None
        except sr.UnknownValueError:
            console.print("[yellow]⚠ Ses anlaşılamadı[/yellow]")
            return None
        except sr.RequestError as e:
            console.print(f"[red]✗ Speech Recognition servisi hatası: {e}[/red]")
            return None
        except Exception as e:
            console.print(f"[red]✗ Dinleme hatası: {e}[/red]")
            return None

    def listen_continuously(self, callback: callable) -> None:
        """
        Sürekli dinleme modu

        Args:
            callback: Her tanınan metin için çağrılacak fonksiyon
        """
        console.print("[cyan]🎤 Sürekli dinleme modu başladı (Ctrl+C ile çık)[/cyan]")

        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source)

                while True:
                    try:
                        audio = self.recognizer.listen(source, timeout=2)
                        text = self.recognizer.recognize_google(
                            audio, language=self.language
                        )
                        callback(text)
                    except sr.WaitTimeoutError:
                        continue
                    except sr.UnknownValueError:
                        continue
                    except Exception as e:
                        console.print(f"[yellow]⚠ Hata: {e}[/yellow]")
                        continue

        except KeyboardInterrupt:
            console.print("\n[cyan]Dinleme durduruldu.[/cyan]")

    def set_language(self, language: str) -> None:
        """Dil ayarını değiştir"""
        self.language = language
        console.print(f"[green]✓ Ses dili: {language}[/green]")

    def enable(self) -> None:
        """Ses arayüzünü aktif et"""
        self.enabled = True
        console.print("[green]✓ Ses arayüzü aktif[/green]")

    def disable(self) -> None:
        """Ses arayüzünü devre dışı bırak"""
        self.enabled = False
        console.print("[yellow]⚠ Ses arayüzü devre dışı[/yellow]")
