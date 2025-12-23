"""
Senaryo 3: Golden Rules Compliance Check

Hesabınızın 5 Altın Kurala uygunluğunu kontrol eder
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.core.constants.golden_rules import GoldenRulesChecker, GoldenRules

console = Console()

console.print(Panel.fit(
    "[bold yellow]⚖️  GOLDEN RULES COMPLIANCE CHECK[/bold yellow]\n"
    "[cyan]5 Altın Kural - Amazon PPC Başarısının Temeli[/cyan]",
    border_style="yellow"
))

# Test Senaryoları
scenarios = [
    {
        "name": "SENARYO A: Başarılı Hesap (Tüm kurallar uyumlu)",
        "data": {
            "current_stock": 500,
            "daily_sales_velocity": 8.0,
            "lead_time_days": 30,
            "budget_spent_percentage": 65.0,
            "current_hour": 18,
            "campaigns_paused": 0,
            "organic_sales": 6000,
            "ppc_sales": 2000,
        },
        "expected": "✓ Uyumlu",
    },
    {
        "name": "SENARYO B: Birden Fazla İhlal",
        "data": {
            "current_stock": 50,  # Düşük stok
            "daily_sales_velocity": 8.0,
            "lead_time_days": 30,
            "budget_spent_percentage": 85.0,  # Bütçe çok hızlı tükeniyor
            "current_hour": 12,
            "campaigns_paused": 2,  # Kampanyalar durmuş
            "organic_sales": 1500,
            "ppc_sales": 2000,  # PPC'ye bağımlı
        },
        "expected": "❌ Çoklu İhlal",
    },
]

for scenario in scenarios:
    console.print(f"\n{'='*70}")
    console.print(f"[bold cyan]{scenario['name']}[/bold cyan]")
    console.print(f"{'='*70}\n")

    # Verileri göster
    data_table = Table(title="Hesap Verileri")
    data_table.add_column("Parametre", style="cyan")
    data_table.add_column("Değer", style="yellow", justify="right")

    data_table.add_row("Mevcut Stok", f"{scenario['data']['current_stock']} birim")
    data_table.add_row("Günlük Satış", f"{scenario['data']['daily_sales_velocity']} birim/gün")
    data_table.add_row("Lead Time", f"{scenario['data']['lead_time_days']} gün")
    data_table.add_row("Bütçe Tüketimi", f"{scenario['data']['budget_spent_percentage']}% (Saat {scenario['data']['current_hour']}:00)")
    data_table.add_row("Durmuş Kampanya", f"{scenario['data']['campaigns_paused']} adet")
    data_table.add_row("Organik Satış", f"${scenario['data']['organic_sales']}")
    data_table.add_row("PPC Satış", f"${scenario['data']['ppc_sales']}")

    console.print(data_table)

    # Compliance check
    console.print(f"\n[bold]Kontrol Ediliyor...[/bold]\n")

    violations = GoldenRulesChecker.check_all(**scenario["data"])

    if not violations:
        console.print(Panel.fit(
            "[bold green]✓ TÜM GOLDEN RULES'A UYUMLU![/bold green]\n"
            "Hesabınız en iyi pratiklere uygun şekilde yönetiliyor.",
            border_style="green"
        ))
    else:
        console.print(Panel.fit(
            f"[bold red]⚠️  {len(violations)} İHLAL TESPİT EDİLDİ![/bold red]\n"
            "Aşağıdaki kurallara uyum sağlanmalı:",
            border_style="red"
        ))

        for idx, violation in enumerate(violations, 1):
            severity_colors = {
                "critical": "red",
                "high": "yellow",
                "medium": "blue",
                "low": "white",
            }
            color = severity_colors.get(violation.severity.value, "white")

            console.print(f"\n[bold {color}]{idx}. KURAL #{violation.rule_number}: {violation.rule_name}[/bold {color}]")
            console.print(f"   [bold]Ciddiyet:[/bold] {violation.severity.value.upper()}")
            console.print(f"   [bold]Mesaj:[/bold] {violation.message}")
            console.print(f"   [bold]Önerilen Aksiyon:[/bold] {violation.recommended_action}")
            console.print(f"   [bold]Etki:[/bold] {violation.impact}")

# Golden Rules Özeti
console.print(f"\n{'='*70}")
console.print("[bold yellow]📚 5 ALTIN KURAL ÖZETİ[/bold yellow]")
console.print(f"{'='*70}\n")

rules_summary = [
    {
        "number": 1,
        "name": "ASLA STOKSUZ KALMA",
        "description": "Minimum 4 haftalık stok tamponu tut",
        "why": "Stok tükenmesi velocity'yi sıfırlar, organik rank'i düşürür, 2-4 hafta toparlanma gerektirir",
    },
    {
        "number": 2,
        "name": "BÜTÇEYI ERKEN TÜKETME",
        "description": "Günlük bütçe saat 18:00'e kadar max %70 harcanmalı",
        "why": "Bütçe erken tükenirse gün boyunca görünmezsin, rakipler domine eder",
    },
    {
        "number": 3,
        "name": "SÜREKLI REKLAM VER",
        "description": "Kampanyaları geçici olarak durdurma",
        "why": "Momentum kırılır, sales velocity düşer, organik rank çöker",
    },
    {
        "number": 4,
        "name": "VERİYE SAYGI GÖSTER",
        "description": "Keyword kararı için min 20 tıklama bekle",
        "why": "Yetersiz veriyle karar hatalı optimizasyona yol açar",
    },
    {
        "number": 5,
        "name": "SEO VE PPC BİRLİKTE ÇALIŞIR",
        "description": "Organic:PPC oranı en az 2:1 olmalı",
        "why": "PPC organik'i besler, organik PPC maliyetini düşürür - sinerjik sistem",
    },
]

for rule in rules_summary:
    console.print(f"[bold yellow]Kural #{rule['number']}:[/bold yellow] {rule['name']}")
    console.print(f"  📋 {rule['description']}")
    console.print(f"  💡 Neden: {rule['why']}\n")

console.print(Panel.fit(
    "[bold cyan]Bu kurallar tartışılamaz![/bold cyan]\n"
    "Her stratejik önerinin temelini oluşturur.\n"
    "Uzun vadeli başarı için mutlaka uyulmalı.",
    border_style="cyan"
))
