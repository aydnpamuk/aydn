"""
JARVIS Prompt Kütüphanesi Yöneticisi

Uzman prompt'ları kaydeder, yükler, günceller ve yönetir.
"""

import json
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table

from .models import ExpertPrompt, Language, PromptLibrary

console = Console()


class PromptLibraryManager:
    """
    Prompt Kütüphanesi Yöneticisi

    JSON tabanlı prompt kütüphanesini yönetir.
    """

    def __init__(self, library_path: Path):
        """
        Args:
            library_path: Kütüphane JSON dosyası yolu
        """
        self.library_path = library_path
        self.library = self._load_library()

    def _load_library(self) -> PromptLibrary:
        """JSON dosyasından kütüphaneyi yükle"""
        if self.library_path.exists():
            try:
                with open(self.library_path, encoding="utf-8") as f:
                    data = json.load(f)
                    return PromptLibrary(**data)
            except Exception as e:
                console.print(f"[yellow]Kütüphane yüklenirken hata: {e}[/yellow]")
                console.print("[yellow]Yeni kütüphane oluşturuluyor...[/yellow]")
        return PromptLibrary()

    def _save_library(self) -> None:
        """Kütüphaneyi JSON dosyasına kaydet"""
        self.library_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.library_path, "w", encoding="utf-8") as f:
            json.dump(
                self.library.model_dump(mode="json"),
                f,
                ensure_ascii=False,
                indent=2,
                default=str,
            )

    def add_prompt(
        self,
        name: str,
        prompt_text: str,
        description: Optional[str] = None,
        tags: Optional[list[str]] = None,
        language: Language = Language.TR,
    ) -> ExpertPrompt:
        """
        Yeni prompt ekle

        Args:
            name: Prompt adı
            prompt_text: Prompt metni
            description: Açıklama (opsiyonel)
            tags: Etiketler (opsiyonel)
            language: Dil (varsayılan: TR)

        Returns:
            Oluşturulan ExpertPrompt

        Raises:
            ValueError: Aynı isimde prompt varsa
        """
        if name in self.library.prompts:
            raise ValueError(f"'{name}' adında bir prompt zaten mevcut!")

        prompt = ExpertPrompt(
            name=name,
            prompt_text=prompt_text,
            description=description,
            tags=tags or [],
            language=language,
        )

        self.library.add_prompt(prompt)
        self._save_library()

        console.print(f"[green]✓ '{name}' prompt'u kaydedildi![/green]")
        return prompt

    def get_prompt(self, name: str) -> Optional[ExpertPrompt]:
        """İsme göre prompt getir"""
        return self.library.get_prompt(name)

    def update_prompt(
        self,
        name: str,
        prompt_text: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[list[str]] = None,
        language: Optional[Language] = None,
    ) -> ExpertPrompt:
        """
        Mevcut prompt'u güncelle

        Args:
            name: Güncellenecek prompt adı
            prompt_text: Yeni prompt metni (opsiyonel)
            description: Yeni açıklama (opsiyonel)
            tags: Yeni etiketler (opsiyonel)
            language: Yeni dil (opsiyonel)

        Returns:
            Güncellenmiş ExpertPrompt

        Raises:
            ValueError: Prompt bulunamazsa
        """
        prompt = self.library.get_prompt(name)
        if not prompt:
            raise ValueError(f"'{name}' adında bir prompt bulunamadı!")

        if prompt_text is not None:
            prompt.prompt_text = prompt_text
        if description is not None:
            prompt.description = description
        if tags is not None:
            prompt.tags = tags
        if language is not None:
            prompt.language = language

        prompt.update_timestamp()
        self._save_library()

        console.print(f"[green]✓ '{name}' prompt'u güncellendi![/green]")
        return prompt

    def delete_prompt(self, name: str) -> bool:
        """
        Prompt sil

        Args:
            name: Silinecek prompt adı

        Returns:
            Başarılı ise True

        Raises:
            ValueError: Prompt bulunamazsa
        """
        if name not in self.library.prompts:
            raise ValueError(f"'{name}' adında bir prompt bulunamadı!")

        success = self.library.delete_prompt(name)
        if success:
            self._save_library()
            console.print(f"[green]✓ '{name}' prompt'u silindi![/green]")
        return success

    def rename_prompt(self, old_name: str, new_name: str) -> ExpertPrompt:
        """
        Prompt'u yeniden adlandır

        Args:
            old_name: Eski ad
            new_name: Yeni ad

        Returns:
            Yeniden adlandırılmış ExpertPrompt

        Raises:
            ValueError: Prompt bulunamazsa veya yeni ad kullanımdaysa
        """
        if old_name not in self.library.prompts:
            raise ValueError(f"'{old_name}' adında bir prompt bulunamadı!")

        if new_name in self.library.prompts:
            raise ValueError(f"'{new_name}' adı zaten kullanımda!")

        prompt = self.library.prompts[old_name]
        prompt.name = new_name
        prompt.update_timestamp()

        del self.library.prompts[old_name]
        self.library.prompts[new_name] = prompt

        # Aktif prompt'u güncelle
        if self.library.active_prompt_name == old_name:
            self.library.active_prompt_name = new_name

        self._save_library()
        console.print(
            f"[green]✓ Prompt '{old_name}' → '{new_name}' olarak yeniden adlandırıldı![/green]"
        )
        return prompt

    def set_active(self, name: Optional[str]) -> bool:
        """
        Aktif prompt'u ayarla

        Args:
            name: Aktif edilecek prompt adı (None = GENEL MOD)

        Returns:
            Başarılı ise True

        Raises:
            ValueError: Prompt bulunamazsa
        """
        if name is not None and name not in self.library.prompts:
            raise ValueError(f"'{name}' adında bir prompt bulunamadı!")

        success = self.library.set_active(name)
        if success:
            self._save_library()
            if name:
                console.print(f"[green]✓ '{name}' aktif prompt olarak ayarlandı![/green]")
            else:
                console.print("[green]✓ GENEL MOD aktif![/green]")
        return success

    def get_active_prompt(self) -> Optional[ExpertPrompt]:
        """Aktif prompt'u getir"""
        return self.library.get_active_prompt()

    def list_prompts(self, show_table: bool = True) -> list[str]:
        """
        Tüm prompt'ları listele

        Args:
            show_table: Rich table olarak göster

        Returns:
            Prompt isimleri listesi
        """
        prompt_names = self.library.list_prompts()

        if show_table and prompt_names:
            table = Table(title="📚 Kayıtlı Prompt'lar")
            table.add_column("İsim", style="cyan")
            table.add_column("Açıklama", style="white")
            table.add_column("Etiketler", style="yellow")
            table.add_column("Dil", style="magenta")
            table.add_column("Aktif", style="green")

            for name in prompt_names:
                prompt = self.library.prompts[name]
                is_active = "✓" if self.library.active_prompt_name == name else ""
                table.add_row(
                    name,
                    prompt.description or "-",
                    ", ".join(prompt.tags) or "-",
                    prompt.language.value,
                    is_active,
                )

            console.print(table)
        elif not prompt_names:
            console.print("[yellow]Henüz kayıtlı prompt yok.[/yellow]")

        return prompt_names

    def search_prompts(self, query: str) -> list[ExpertPrompt]:
        """
        Prompt'larda arama yap

        Args:
            query: Arama sorgusu (isim, açıklama, etiketlerde arar)

        Returns:
            Eşleşen prompt'lar
        """
        query_lower = query.lower()
        results = []

        for prompt in self.library.prompts.values():
            if (
                query_lower in prompt.name.lower()
                or (prompt.description and query_lower in prompt.description.lower())
                or any(query_lower in tag.lower() for tag in prompt.tags)
            ):
                results.append(prompt)

        return results
