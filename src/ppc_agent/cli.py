"""Amazon PPC Vaka Avcısı - CLI Komutları."""

import argparse
import sys
from datetime import datetime

from rich.console import Console

from .friday_agent import FridayAnalyzer
from .monday_agent import MondayScanner
from .storage import CaseLibrary, get_current_week_id


def scan_command(args):
    """Pazartesi hızlı tarama komutu."""
    console = Console()
    console.print("\n[bold cyan]🔍 Amazon PPC Vaka Avcısı - Pazartesi Tarama[/bold cyan]\n")

    library = CaseLibrary(args.library_path)
    scanner = MondayScanner(library)

    candidates = scanner.run_weekly_scan(days_back=args.days)

    console.print(f"\n[green]✅ Tarama tamamlandı! {len(candidates)} aday bulundu.[/green]")
    console.print(f"[dim]Veriler kaydedildi: {library.library_path}[/dim]\n")


def analyze_command(args):
    """Cuma derin analiz komutu."""
    console = Console()
    console.print("\n[bold magenta]🔬 Amazon PPC Vaka Avcısı - Derin Analiz[/bold magenta]\n")

    library = CaseLibrary(args.library_path)
    analyzer = FridayAnalyzer(library)

    if args.url:
        # Tek URL analizi
        case = analyzer.analyze_case(args.url, title=args.title)
        if case:
            console.print(f"\n[green]✅ Analiz tamamlandı! Vaka ID: {case.case_id}[/green]")
    else:
        console.print("[yellow]⚠️  Lütfen --url parametresi ile analiz edilecek URL'i belirtin.[/yellow]")
        sys.exit(1)


def report_command(args):
    """Rapor oluşturma komutu."""
    console = Console()
    console.print("\n[bold blue]📊 Amazon PPC Vaka Avcısı - Raporlar[/bold blue]\n")

    library = CaseLibrary(args.library_path)

    if args.stats:
        # Kütüphane istatistikleri
        stats = library.get_statistics()
        console.print("[bold]Kütüphane İstatistikleri:[/bold]\n")
        console.print(f"  📁 Toplam Aday Vaka: {stats['total_candidates']}")
        console.print(f"  📚 Toplam Derin Analiz: {stats['total_cases']}")
        console.print(f"  📋 Toplam Rapor: {stats['total_reports']}")
        console.print(f"  ⭐ Ortalama Güven Puanı: {stats['average_confidence_score']}/100")
        console.print(f"  📂 Kütüphane Yolu: {stats['library_path']}\n")

    if args.week:
        # Haftalık rapor
        week_id = args.week if args.week != "current" else get_current_week_id()
        report = library.load_weekly_report(week_id)

        if report:
            console.print(f"[bold]Haftalık Rapor - {week_id}[/bold]\n")
            console.print(f"  📅 Hafta: {report.week_start.strftime('%Y-%m-%d')} - {report.week_end.strftime('%Y-%m-%d')}")
            console.print(f"  🔍 Pazartesi Tarması: {report.candidates_found} aday")
            console.print(f"  🔬 Cuma Analizi: {report.cases_analyzed} derin analiz")
            console.print(f"\n  🏆 Top 3 Öneriler:")
            for i, url in enumerate(report.top_3_for_friday, 1):
                console.print(f"     {i}. {url}")
        else:
            console.print(f"[yellow]⚠️  {week_id} için rapor bulunamadı.[/yellow]")

    if args.list:
        # Vaka listesi
        cases = library.load_case_studies(limit=args.limit)
        console.print(f"[bold]Son {len(cases)} Derin Analiz Vakası:[/bold]\n")

        for i, case in enumerate(cases, 1):
            console.print(f"{i}. [{case.tags_confidence.value}] {case.title}")
            console.print(f"   ID: {case.case_id} | Güven: {case.confidence_score.total}/100")
            console.print(f"   URL: {case.url}\n")


def search_command(args):
    """Vaka arama komutu."""
    console = Console()
    console.print("\n[bold green]🔎 Amazon PPC Vaka Avcısı - Arama[/bold green]\n")

    library = CaseLibrary(args.library_path)

    results = library.search_cases(
        market=args.market,
        category=args.category,
        min_confidence=args.min_confidence,
    )

    console.print(f"[bold]Arama Sonuçları: {len(results)} vaka bulundu[/bold]\n")

    for i, case in enumerate(results[:args.limit], 1):
        console.print(f"{i}. {case.title}")
        console.print(f"   Pazar: {case.market.value} | Kategori: {case.product_category.value}")
        console.print(f"   Güven: {case.confidence_score.total}/100 | ID: {case.case_id}")
        console.print(f"   URL: {case.url}\n")


def main():
    """Ana CLI giriş noktası."""
    parser = argparse.ArgumentParser(
        description="Amazon PPC Vaka Avcısı - Gerçek PPC vakalarını bul ve analiz et"
    )

    parser.add_argument(
        "--library-path",
        default="data/case_library",
        help="Kütüphane veri dizini (varsayılan: data/case_library)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Komutlar")

    # SCAN komutu
    scan_parser = subparsers.add_parser("scan", help="Pazartesi hızlı tarama (20 dk)")
    scan_parser.add_argument(
        "--days", type=int, default=7, help="Kaç gün geriye git (varsayılan: 7)"
    )

    # ANALYZE komutu
    analyze_parser = subparsers.add_parser("analyze", help="Cuma derin analiz (1 saat)")
    analyze_parser.add_argument("--url", required=True, help="Analiz edilecek vaka URL'i")
    analyze_parser.add_argument("--title", help="Vaka başlığı (opsiyonel)")

    # REPORT komutu
    report_parser = subparsers.add_parser("report", help="Raporlar ve istatistikler")
    report_parser.add_argument(
        "--stats", action="store_true", help="Kütüphane istatistiklerini göster"
    )
    report_parser.add_argument(
        "--week", help="Haftalık rapor (ör. 2025-W01 veya 'current')"
    )
    report_parser.add_argument(
        "--list", action="store_true", help="Vaka listesini göster"
    )
    report_parser.add_argument(
        "--limit", type=int, default=10, help="Maksimum sonuç sayısı (varsayılan: 10)"
    )

    # SEARCH komutu
    search_parser = subparsers.add_parser("search", help="Kütüphanede arama yap")
    search_parser.add_argument("--market", help="Pazar filtresi (ör. US, EU, DE)")
    search_parser.add_argument("--category", help="Kategori filtresi")
    search_parser.add_argument(
        "--min-confidence", type=int, help="Minimum güven puanı (0-100)"
    )
    search_parser.add_argument(
        "--limit", type=int, default=10, help="Maksimum sonuç sayısı (varsayılan: 10)"
    )

    args = parser.parse_args()

    if args.command == "scan":
        scan_command(args)
    elif args.command == "analyze":
        analyze_command(args)
    elif args.command == "report":
        report_command(args)
    elif args.command == "search":
        search_command(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
