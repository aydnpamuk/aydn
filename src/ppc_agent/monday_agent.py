"""Amazon PPC Vaka Avcısı - Pazartesi Tarama Ajanı."""

from datetime import datetime, timedelta

from rich.console import Console
from rich.table import Table

from .models import CaseCandidate
from .scrapers import BlogScraper, CaseAnalyzer, RedditScraper
from .storage import CaseLibrary


class MondayScanner:
    """Pazartesi hızlı tarama ajanı - 20 dakikada 8-15 aday bul."""

    def __init__(self, library: CaseLibrary):
        """
        Tarama ajanı başlatıcı.

        Args:
            library: Vaka kütüphanesi
        """
        self.library = library
        self.reddit_scraper = RedditScraper()
        self.blog_scraper = BlogScraper()
        self.console = Console()

        # Varsayılan kaynaklar
        self.subreddits = ["FulfillmentByAmazon", "AmazonSeller"]
        self.blog_urls = [
            "https://advertising.amazon.com/blog",
            # Daha fazla blog URL'si eklenebilir
        ]

    def run_weekly_scan(self, days_back: int = 7) -> list[CaseCandidate]:
        """
        Haftalık hızlı tarama yap.

        Args:
            days_back: Kaç gün geriye git

        Returns:
            Aday vaka listesi
        """
        self.console.print(
            f"\n[bold blue]🔍 Pazartesi Tarama Başlıyor[/bold blue] - {datetime.now().strftime('%Y-%m-%d')}\n"
        )

        candidates = []

        # 1. Reddit Taraması
        self.console.print("[yellow]📱 Reddit taranıyor...[/yellow]")
        reddit_posts = self.reddit_scraper.search_ppc_cases(
            self.subreddits, days_back=days_back, limit=50
        )

        for post in reddit_posts:
            candidate = CaseAnalyzer.create_candidate_from_reddit(post)
            if candidate:
                candidates.append(candidate)
                self.library.save_candidate(candidate)

        self.console.print(f"   ✓ Reddit'ten {len(candidates)} aday bulundu\n")

        # 2. Blog Taraması
        self.console.print("[yellow]📝 Bloglar taranıyor...[/yellow]")
        blog_posts = self.blog_scraper.fetch_blog_posts(self.blog_urls)

        blog_count = 0
        for post in blog_posts:
            candidate = CaseAnalyzer.create_candidate_from_blog(post)
            if candidate:
                candidates.append(candidate)
                self.library.save_candidate(candidate)
                blog_count += 1

        self.console.print(f"   ✓ Bloglardan {blog_count} aday bulundu\n")

        # 3. Sonuçları sırala (güven puanına göre)
        candidates.sort(key=lambda x: x.preliminary_confidence, reverse=True)

        # 4. Özet göster
        self._display_summary(candidates)

        return candidates

    def _display_summary(self, candidates: list[CaseCandidate]) -> None:
        """
        Tarama özeti göster.

        Args:
            candidates: Aday listesi
        """
        self.console.print(
            f"\n[bold green]✅ Tarama Tamamlandı![/bold green] Toplam {len(candidates)} aday bulundu.\n"
        )

        if not candidates:
            self.console.print("[yellow]⚠️  Hiç aday bulunamadı.[/yellow]")
            return

        # Top 3 göster
        top_3 = candidates[:3]

        self.console.print("[bold cyan]🏆 Cuma İçin Top 3 Öneri:[/bold cyan]\n")

        for i, candidate in enumerate(top_3, 1):
            self.console.print(f"[bold]{i}. {candidate.title}[/bold]")
            self.console.print(f"   URL: {candidate.url}")
            self.console.print(f"   Platform: {candidate.platform.value}")
            self.console.print(f"   Güven: {candidate.preliminary_confidence}/100")
            self.console.print(
                f"   Metrikler: {', '.join(candidate.visible_metrics) if candidate.visible_metrics else 'YOK'}"
            )
            self.console.print(
                f"   Önce/Sonra: {'✓ Var' if candidate.has_before_after else '✗ Yok'}"
            )
            self.console.print(f"   Neden: {candidate.confidence_reason}\n")

        # Detaylı tablo
        self._display_candidates_table(candidates)

    def _display_candidates_table(self, candidates: list[CaseCandidate]) -> None:
        """
        Aday listesini tablo olarak göster.

        Args:
            candidates: Aday listesi
        """
        table = Table(title="Haftalık Aday Listesi", show_lines=True)

        table.add_column("No", style="cyan", width=4)
        table.add_column("Başlık", style="white", width=40)
        table.add_column("Platform", width=10)
        table.add_column("Metrik", width=8)
        table.add_column("Ö/S", width=5)
        table.add_column("Güven", width=6)

        for i, candidate in enumerate(candidates[:15], 1):  # İlk 15
            table.add_row(
                str(i),
                candidate.title[:40],
                candidate.platform.value,
                str(len(candidate.visible_metrics)),
                "✓" if candidate.has_before_after else "✗",
                f"{candidate.preliminary_confidence}/100",
            )

        self.console.print(table)

    def get_top_candidates(
        self, candidates: list[CaseCandidate], count: int = 3
    ) -> list[str]:
        """
        Top N adayın URL'lerini getir.

        Args:
            candidates: Aday listesi
            count: Kaç aday

        Returns:
            URL listesi
        """
        return [str(c.url) for c in candidates[:count]]
