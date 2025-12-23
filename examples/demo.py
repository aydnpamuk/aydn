"""
Amazon PPC System - Demo Script

Demonstrates key features of the system
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.core.metrics.calculator import MetricsCalculator
from src.core.benchmarks.standards import BenchmarkEvaluator
from src.core.formulas.bid_optimization import RPCBidOptimizer
from src.decision.acos.manager import ACoSDecisionTree
from src.crisis.stockout.protocol import StockoutProtocol
from src.core.constants.golden_rules import GoldenRulesChecker

console = Console()


def demo_metrics():
    """Demo: Calculate PPC Metrics"""
    console.print("\n[bold cyan]1. PPC METRICS CALCULATION[/bold cyan]\n")

    # Calculate metrics
    result = MetricsCalculator.calculate(
        ad_spend=500,
        ad_sales=2000,
        total_sales=5000,
        impressions=10000,
        clicks=100,
        orders=10,
    )

    console.print(f"Ad Spend: ${result.ad_spend}")
    console.print(f"Ad Sales: ${result.ad_sales}")
    console.print(f"Total Sales: ${result.total_sales}")
    console.print(f"\n[green]ACoS: {result.acos:.2f}%[/green]")
    console.print(f"[green]TACOS: {result.tacos:.2f}%[/green]")
    console.print(f"[green]CTR: {result.ctr:.3f}%[/green]")
    console.print(f"[green]CVR: {result.cvr:.2f}%[/green]")
    console.print(f"[green]RPC: ${result.rpc:.2f}[/green]")


def demo_bid_optimization():
    """Demo: RPC-Based Bid Optimization"""
    console.print("\n[bold cyan]2. BID OPTIMIZATION (RPC FORMULA)[/bold cyan]\n")

    # Calculate optimal bid
    optimal_bid = RPCBidOptimizer.calculate_optimal_bid(
        total_sales=1000,
        total_clicks=200,
        target_acos=0.25,
    )

    console.print(f"Total Sales: $1,000")
    console.print(f"Total Clicks: 200")
    console.print(f"RPC: $5.00")
    console.print(f"Target ACoS: 25%")
    console.print(f"\n[green]Optimal Bid: ${optimal_bid:.2f}[/green]")

    # Get bid recommendation
    recommendation = RPCBidOptimizer.recommend_bid_adjustment(
        current_bid=2.0,
        total_sales=1000,
        total_clicks=200,
        target_acos=0.25,
        current_acos=0.40,
    )

    console.print(f"\nCurrent Bid: $2.00")
    console.print(f"Current ACoS: 40%")
    console.print(f"[yellow]Recommended Bid: ${recommendation.recommended_bid:.2f}[/yellow]")
    console.print(f"[yellow]Change: {recommendation.change_percentage:.1f}%[/yellow]")
    console.print(f"Reason: {recommendation.reason}")


def demo_acos_decision_tree():
    """Demo: ACoS Decision Tree"""
    console.print("\n[bold cyan]3. ACOS DECISION TREE[/bold cyan]\n")

    # Scenario 1: Unprofitable
    console.print("[bold]Scenario 1: Unprofitable (ACoS > 100%)[/bold]")
    decision = ACoSDecisionTree.evaluate(
        acos=120.0,
        clicks=25,
        cvr=12.0,
    )
    console.print(f"Action: [red]{decision.action.value}[/red]")
    console.print(f"Reason: {decision.reason}\n")

    # Scenario 2: Excellent (Scale opportunity)
    console.print("[bold]Scenario 2: Excellent (ACoS < 15%)[/bold]")
    decision = ACoSDecisionTree.evaluate(
        acos=10.0,
        clicks=50,
        cvr=12.0,
        target_acos=25.0,
    )
    console.print(f"Action: [green]{decision.action.value}[/green]")
    console.print(f"Reason: {decision.reason}\n")


def demo_stockout_protocol():
    """Demo: Stockout Crisis Protocol"""
    console.print("\n[bold cyan]4. STOCKOUT CRISIS PROTOCOL[/bold cyan]\n")

    # Analyze stock
    analysis = StockoutProtocol.analyze_stock_situation(
        current_stock=50,
        daily_velocity=5.0,
        lead_time_days=30,
    )

    console.print(f"Current Stock: {analysis.current_stock} units")
    console.print(f"Daily Velocity: {analysis.daily_velocity:.1f} units/day")
    console.print(f"Days Remaining: [yellow]{analysis.days_remaining:.1f} days[/yellow]")
    console.print(f"Stock Level: [red]{analysis.stock_level.value.upper()}[/red]")

    if analysis.recommended_actions:
        console.print("\n[bold]Recommended Actions:[/bold]")
        for action in analysis.recommended_actions[:2]:
            console.print(f"• [{action.priority.value.upper()}] {action.action}")


def demo_golden_rules():
    """Demo: Golden Rules Checker"""
    console.print("\n[bold cyan]5. GOLDEN RULES COMPLIANCE CHECK[/bold cyan]\n")

    # Check all rules
    violations = GoldenRulesChecker.check_all(
        current_stock=50,
        daily_sales_velocity=5.0,
        lead_time_days=30,
        budget_spent_percentage=85.0,
        current_hour=12,
        campaigns_paused=0,
        organic_sales=3000,
        ppc_sales=2000,
    )

    if violations:
        console.print("[red]⚠️  VIOLATIONS DETECTED[/red]\n")
        for violation in violations:
            console.print(f"[bold]Rule #{violation.rule_number}: {violation.rule_name}[/bold]")
            console.print(f"Severity: {violation.severity.value.upper()}")
            console.print(f"Message: {violation.message}")
            console.print(f"Action: {violation.recommended_action}\n")
    else:
        console.print("[green]✓ All Golden Rules Compliant[/green]")


def demo_benchmark_evaluation():
    """Demo: Benchmark Evaluation"""
    console.print("\n[bold cyan]6. BENCHMARK EVALUATION[/bold cyan]\n")

    # Evaluate metrics against benchmarks
    evaluation = BenchmarkEvaluator.evaluate_all(
        ctr_ppc=0.65,
        cvr=12.0,
        acos=28.0,
        tacos=10.0,
        organic_sales=3000,
        ppc_sales=2000,
    )

    table = Table(title="Performance Evaluation")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_column("Level", style="yellow")

    if "ctr_ppc" in evaluation:
        table.add_row(
            "PPC CTR",
            f"{evaluation['ctr_ppc']['value']:.3f}%",
            evaluation["ctr_ppc"]["level"].value,
        )

    if "cvr" in evaluation:
        table.add_row(
            "CVR",
            f"{evaluation['cvr']['value']:.1f}%",
            evaluation["cvr"]["level"].value,
        )

    if "acos" in evaluation:
        table.add_row(
            "ACoS",
            f"{evaluation['acos']['value']:.1f}%",
            evaluation["acos"]["level"].value,
        )

    if "tacos" in evaluation:
        table.add_row(
            "TACOS",
            f"{evaluation['tacos']['value']:.1f}%",
            evaluation["tacos"]["strategy"],
        )

    if "organic_ppc_ratio" in evaluation:
        ratio = evaluation["organic_ppc_ratio"]["ratio"]
        health = evaluation["organic_ppc_ratio"]["health"]
        table.add_row("Organic:PPC", f"{ratio:.1f}:1", health)

    console.print(table)


def main():
    """Run all demos"""
    console.print(
        Panel.fit(
            "[bold white]Amazon PPC & SEO Management System[/bold white]\n"
            "[cyan]Professional Demo[/cyan]\n"
            "Based on Amazon PPC & SEO Bible v3.0",
            border_style="green",
        )
    )

    demo_metrics()
    demo_bid_optimization()
    demo_acos_decision_tree()
    demo_stockout_protocol()
    demo_golden_rules()
    demo_benchmark_evaluation()

    console.print(
        Panel.fit(
            "[bold green]✓ Demo Complete[/bold green]\n"
            "For more features, try: python -m src.cli.app --help",
            border_style="green",
        )
    )


if __name__ == "__main__":
    main()
