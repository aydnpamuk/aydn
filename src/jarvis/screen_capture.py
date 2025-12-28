"""
JARVIS Ekran Yakalama Modülü

Ekran görüntüsü yakalama ve kaydetme işlemlerini yönetir.
"""

import base64
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Optional

import mss
from PIL import Image
from rich.console import Console

from .models import ScreenCapture

console = Console()


class ScreenCaptureManager:
    """
    Ekran Yakalama Yöneticisi

    Ekran görüntüsü alır ve kaydeder.
    """

    def __init__(self, screenshots_path: Path):
        """
        Args:
            screenshots_path: Ekran görüntülerinin kaydedileceği klasör
        """
        self.screenshots_path = screenshots_path
        self.screenshots_path.mkdir(parents=True, exist_ok=True)

    def capture_screen(
        self,
        region: Optional[tuple[int, int, int, int]] = None,
        save: bool = True,
    ) -> tuple[Image.Image, Optional[ScreenCapture]]:
        """
        Ekran görüntüsü yakala

        Args:
            region: Yakalanacak bölge (x, y, width, height). None ise tüm ekran
            save: True ise dosyaya kaydet

        Returns:
            (PIL Image, ScreenCapture model)
        """
        try:
            with mss.mss() as sct:
                if region:
                    # Belirli bir bölge
                    monitor = {
                        "left": region[0],
                        "top": region[1],
                        "width": region[2],
                        "height": region[3],
                    }
                else:
                    # Tüm ekran (birincil monitör)
                    monitor = sct.monitors[1]

                screenshot = sct.grab(monitor)
                img = Image.frombytes(
                    "RGB", (screenshot.width, screenshot.height), screenshot.rgb
                )

                screen_capture_model = None
                if save:
                    screen_capture_model = self._save_screenshot(img)

                console.print(
                    f"[green]✓ Ekran görüntüsü yakalandı: {img.width}x{img.height}[/green]"
                )
                return img, screen_capture_model

        except Exception as e:
            console.print(f"[red]✗ Ekran yakalama hatası: {e}[/red]")
            raise

    def _save_screenshot(self, img: Image.Image) -> ScreenCapture:
        """
        Ekran görüntüsünü dosyaya kaydet

        Args:
            img: PIL Image

        Returns:
            ScreenCapture model
        """
        timestamp = datetime.now()
        filename = timestamp.strftime("screenshot_%Y%m%d_%H%M%S.png")
        filepath = self.screenshots_path / filename

        img.save(filepath, "PNG")

        screen_capture = ScreenCapture(
            timestamp=timestamp,
            image_path=filepath,
            width=img.width,
            height=img.height,
        )

        console.print(f"[green]✓ Ekran görüntüsü kaydedildi: {filepath}[/green]")
        return screen_capture

    def capture_to_base64(
        self, region: Optional[tuple[int, int, int, int]] = None
    ) -> str:
        """
        Ekran görüntüsünü base64 string olarak al

        Vision API'lara göndermek için kullanılır.

        Args:
            region: Yakalanacak bölge (x, y, width, height). None ise tüm ekran

        Returns:
            Base64 encoded PNG string
        """
        img, _ = self.capture_screen(region=region, save=False)

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_bytes = buffer.getvalue()

        return base64.b64encode(img_bytes).decode("utf-8")

    def get_screen_info(self) -> dict:
        """
        Ekran bilgilerini al

        Returns:
            Monitör bilgileri dict
        """
        with mss.mss() as sct:
            monitors = sct.monitors
            return {
                "monitor_count": len(monitors) - 1,  # İlk eleman summary
                "primary_monitor": monitors[1] if len(monitors) > 1 else None,
                "all_monitors": monitors[1:],  # Summary hariç
            }
