"""
Senaryo 2: Stok Krizi Yönetimi

Farklı stok seviyelerinde ne yapılması gerektiğini gösterir
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from datetime import datetime

from src.crisis.stockout.protocol import StockoutProtocol, StockLevel

console = Console()

console.print(Panel.fit(
    "[bold red]🚨 STOK KRİZİ YÖNETİMİ[/bold red]\n"
    "[yellow]GOLDEN RULE #1: NEVER RUN OUT OF STOCK[/yellow]",
    border_style="red"
))

# Test senaryoları
scenarios = [
    {
        "name": "SENARYO A: Sağlıklı Stok",
        "stock": 500,
        "velocity": 8.0,
        "lead_time": 30,
        "color": "green",
    },
    {
        "name": "SENARYO B: Uyarı Seviyesi",
        "stock": 120,
        "velocity": 8.0,
        "lead_time": 30,
        "color": "yellow",
    },
    {
        "name": "SENARYO C: Kritik Seviye",
        "stock": 65,
        "velocity": 8.0,
        "lead_time": 30,
        "color": "red",
    },
    {
        "name": "SENARYO D: ACİL DURUM",
        "stock": 30,
        "velocity": 8.0,
        "lead_time": 30,
        "color": "red",
    },
]

for scenario in scenarios:
    console.print(f"\n[bold {scenario['color']}]{'='*70}[/bold {scenario['color']}]")
    console.print(f"[bold {scenario['color']}]{scenario['name']}[/bold {scenario['color']}]")
    console.print(f"[bold {scenario['color']}]{'='*70}[/bold {scenario['color']}]\n")

    # Stok analizi
    analysis = StockoutProtocol.analyze_stock_situation(
        current_stock=scenario["stock"],
        daily_velocity=scenario["velocity"],
        lead_time_days=scenario["lead_time"],
    )

    # Durum Tablosu
    table = Table(title="Stok Durumu")
    table.add_column("Özellik", style="cyan")
    table.add_column("Değer", style=scenario["color"], justify="right")

    table.add_row("Mevcut Stok", f"{analysis.current_stock} birim")
    table.add_row("Günlük Satış Hızı", f"{analysis.daily_velocity:.1f} birim/gün")
    table.add_row("Kalan Gün", f"{analysis.days_remaining:.1f} gün")
    table.add_row("Durum", analysis.stock_level.value.upper())

    if analysis.estimated_stockout_date:
        table.add_row(
            "Tahmini Tükenme",
            analysis.estimated_stockout_date.strftime("%d %B %Y")
        )

    console.print(table)

    # PPC Önerisi
    should_pause = StockoutProtocol.should_pause_ppc(analysis.days_remaining)
    budget_multiplier = StockoutProtocol.calculate_budget_reduction(analysis.days_remaining)

    console.print(f"\n[bold]PPC Önerisi:[/bold]")
    if should_pause:
        console.print("[red bold]⚠️  TÜM PPC KAMPANYALARINI DURDUR[/red bold]")
    elif budget_multiplier < 1.0:
        reduction = (1 - budget_multiplier) * 100
        console.print(f"[yellow]⚠️  PPC bütçesini %{reduction:.0f} azalt[/yellow]")
    else:
        console.print("[green]✓ Normal PPC operasyonlarına devam[/green]")

    # Aksiyon Planı
    if analysis.recommended_actions:
        console.print(f"\n[bold]Aksiyon Planı:[/bold]")
        for idx, action in enumerate(analysis.recommended_actions, 1):
            priority_icons = {
                "immediate": "🔴",
                "short_term": "🟡",
                "medium_term": "🔵",
            }
            icon = priority_icons.get(action.priority.value, "⚪")

            console.print(f"\n{icon} [bold]{idx}. {action.priority.value.upper()}[/bold]")
            console.print(f"   Aksiyon: {action.action}")
            console.print(f"   Neden: {action.reason}")

            if action.deadline:
                console.print(f"   Son Tarih: {action.deadline.strftime('%d/%m/%Y %H:%M')}")

    # Reorder Point Hesaplama
    reorder_point = StockoutProtocol.calculate_reorder_point(
        daily_velocity=scenario["velocity"],
        lead_time_days=scenario["lead_time"],
        safety_stock_weeks=2,
    )

    console.print(f"\n[bold cyan]📋 Reorder Point: {reorder_point} birim[/bold cyan]")
    console.print(f"   (Stok bu seviyeye düştüğünde yeni sipariş ver)")

# Özet ve En İyi Pratikler
console.print(f"\n[bold green]{'='*70}[/bold green]")
console.print("[bold green]📚 EN İYİ PRATİKLER[/bold green]")
console.print(f"[bold green]{'='*70}[/bold green]\n")

best_practices = [
    "✓ Minimum 4 haftalık stok tamponu tut",
    "✓ Reorder point alerts kur",
    "✓ Formül: Sales velocity × Lead time + Safety stock",
    "✓ FBM backup planı hazır tut",
    "✓ Günlük stok takibi yap",
    "✓ Tedarikçi ile iyi ilişki kur (acil durumlar için)",
]

for practice in best_practices:
    console.print(f"  {practice}")

console.print(f"\n[bold red]⚠️  HATIRLA: Stok tükenmesi 2-4 haftalık toparlanma süresi gerektirir![/bold red]")
console.print("[bold red]   Organik rank düşer, PPC performansı sıfırlanır, rakipler boşluğu doldurur.[/bold red]")
