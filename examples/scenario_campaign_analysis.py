"""
Senaryo 1: Kampanya Performans Analizi ve Optimizasyon

Gerçek kampanya verisiyle detaylı analiz
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.core.metrics.calculator import MetricsCalculator
from src.core.benchmarks.standards import BenchmarkEvaluator
from src.core.formulas.bid_optimization import RPCBidOptimizer
from src.decision.acos.manager import ACoSDecisionTree

console = Console()

# Kampanya Verileri
CAMPAIGN_DATA = {
    "name": "SP - Leather Wallet - Manual Exact",
    "ad_spend": 1250,
    "ad_sales": 3500,
    "total_sales": 8000,
    "impressions": 45000,
    "clicks": 180,
    "orders": 21,
    "current_bid": 7.50,
    "target_acos": 0.25,  # 25%
}

console.print(Panel.fit(
    f"[bold cyan]Kampanya:[/bold cyan] {CAMPAIGN_DATA['name']}\n"
    f"[bold]Hedef ACoS:[/bold] {CAMPAIGN_DATA['target_acos']*100:.0f}%",
    border_style="blue"
))

# 1. Metrik Hesaplama
console.print("\n[bold yellow]📊 1. METRIK ANALİZİ[/bold yellow]\n")

metrics = MetricsCalculator.calculate(
    ad_spend=CAMPAIGN_DATA["ad_spend"],
    ad_sales=CAMPAIGN_DATA["ad_sales"],
    total_sales=CAMPAIGN_DATA["total_sales"],
    impressions=CAMPAIGN_DATA["impressions"],
    clicks=CAMPAIGN_DATA["clicks"],
    orders=CAMPAIGN_DATA["orders"],
)

table = Table(title="Kampanya Metrikleri")
table.add_column("Metrik", style="cyan")
table.add_column("Değer", style="green", justify="right")
table.add_column("Durum", style="yellow")

table.add_row("ACoS", f"{metrics.acos:.2f}%",
              "❌ Hedefin üstünde (25% hedef)" if float(metrics.acos) > 25 else "✓ Hedefte")
table.add_row("TACOS", f"{metrics.tacos:.2f}%",
              "Agresif büyüme" if float(metrics.tacos) > 12 else "Sağlıklı")
table.add_row("CTR", f"{metrics.ctr:.3f}%",
              "Listing optimizasyonu gerekebilir" if float(metrics.ctr) < 0.5 else "✓ İyi")
table.add_row("CVR", f"{metrics.cvr:.2f}%",
              "✓ İyi performans")
table.add_row("CPC", f"${metrics.cpc:.2f}", "Yüksek")

console.print(table)

# 2. ACoS Karar Ağacı
console.print("\n[bold yellow]🌳 2. ACOS KARAR AĞACI[/bold yellow]\n")

decision = ACoSDecisionTree.evaluate(
    acos=float(metrics.acos),
    clicks=CAMPAIGN_DATA["clicks"],
    cvr=float(metrics.cvr),
    target_acos=CAMPAIGN_DATA["target_acos"] * 100,
)

console.print(f"[bold]Karar:[/bold] {decision.action.value}")
console.print(f"[bold]Güven:[/bold] {decision.confidence.value}")
console.print(f"[bold]Açıklama:[/bold] {decision.reason}\n")

# 3. Bid Optimizasyonu (RPC Formülü)
console.print("\n[bold yellow]💰 3. BID OPTİMİZASYONU (RPC FORMÜLÜ)[/bold yellow]\n")

bid_recommendation = RPCBidOptimizer.recommend_bid_adjustment(
    current_bid=CAMPAIGN_DATA["current_bid"],
    total_sales=CAMPAIGN_DATA["ad_sales"],
    total_clicks=CAMPAIGN_DATA["clicks"],
    target_acos=CAMPAIGN_DATA["target_acos"],
    current_acos=float(metrics.acos) / 100,
)

console.print(f"[bold]Mevcut Bid:[/bold] ${bid_recommendation.current_bid:.2f}")
console.print(f"[bold green]Önerilen Bid:[/bold green] ${bid_recommendation.recommended_bid:.2f}")
console.print(f"[bold]Değişim:[/bold] {bid_recommendation.change_percentage:.1f}%")
console.print(f"[bold]Açıklama:[/bold] {bid_recommendation.reason}")
console.print(f"[bold]Güven Seviyesi:[/bold] {bid_recommendation.confidence}\n")

# 4. Hesaplama Detayları
console.print("\n[bold yellow]🔢 4. HESAPLAMA DETAYLARI[/bold yellow]\n")

rpc = CAMPAIGN_DATA["ad_sales"] / CAMPAIGN_DATA["clicks"]
optimal_bid_manual = rpc * CAMPAIGN_DATA["target_acos"]

console.print(f"RPC = Ad Sales / Clicks")
console.print(f"RPC = ${CAMPAIGN_DATA['ad_sales']} / {CAMPAIGN_DATA['clicks']}")
console.print(f"[green]RPC = ${rpc:.2f}[/green]\n")

console.print(f"Optimal Bid = RPC × Target ACoS")
console.print(f"Optimal Bid = ${rpc:.2f} × {CAMPAIGN_DATA['target_acos']}")
console.print(f"[green]Optimal Bid = ${optimal_bid_manual:.2f}[/green]\n")

# 5. Aksiyon Planı
console.print("\n[bold yellow]📋 5. AKSİYON PLANI[/bold yellow]\n")

actions = []

if float(metrics.acos) > 25:
    actions.append("1. ⚠️  Bid'i ${:.2f} → ${:.2f} düşür ({}% azalış)".format(
        CAMPAIGN_DATA["current_bid"],
        float(bid_recommendation.recommended_bid),
        abs(float(bid_recommendation.change_percentage))
    ))

if float(metrics.ctr) < 0.5:
    actions.append("2. 🖼️  Ana görseli optimize et (CTR düşük)")

if float(metrics.tacos) > 12:
    actions.append("3. 📈 SEO'yu güçlendir (Organic:PPC oranı düşük)")

actions.append("4. 📊 7 gün sonra metrikleri tekrar değerlendir")

for action in actions:
    console.print(f"  {action}")

# 6. Beklenen Sonuçlar
console.print("\n[bold yellow]🎯 6. BEKLENİLEN SONUÇLAR (Bid Ayarlaması Sonrası)[/bold yellow]\n")

new_bid = float(bid_recommendation.recommended_bid)
current_cpc = float(metrics.cpc)
estimated_new_cpc = new_bid * 0.85  # Bid azalınca CPC de azalır

estimated_new_acos = (estimated_new_cpc * CAMPAIGN_DATA["clicks"]) / CAMPAIGN_DATA["ad_sales"] * 100

console.print(f"Mevcut CPC: ${current_cpc:.2f}")
console.print(f"Tahmini Yeni CPC: [green]${estimated_new_cpc:.2f}[/green]")
console.print(f"\nMevcut ACoS: {float(metrics.acos):.1f}%")
console.print(f"Tahmini Yeni ACoS: [green]{estimated_new_acos:.1f}%[/green] (Hedef: 25%)")

if estimated_new_acos <= 25:
    console.print("\n[bold green]✓ Hedefe ulaşılması bekleniyor![/bold green]")
else:
    console.print(f"\n[yellow]⚠️  Hedefe yaklaşılacak ama ek optimizasyon gerekebilir[/yellow]")

console.print("\n" + "="*60)
console.print("[bold cyan]Analiz tamamlandı![/bold cyan]")
