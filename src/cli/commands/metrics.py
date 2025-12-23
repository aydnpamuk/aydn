"""
Metrics CLI Commands

Commands for calculating and displaying PPC metrics
"""

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from ...core.metrics.calculator import MetricsCalculator
from ...core.benchmarks.standards import BenchmarkEvaluator

app = typer.Typer(help="Calculate PPC metrics")
console = Console()


@app.command()
def calculate(
    ad_spend: float = typer.Option(..., help="Advertising spend amount"),
    ad_sales: float = typer.Option(..., help="Sales from advertising"),
    total_sales: float = typer.Option(..., help="Total sales (organic + ads)"),
    impressions: int = typer.Option(None, help="Number of impressions"),
    clicks: int = typer.Option(None, help="Number of clicks"),
    orders: int = typer.Option(None, help="Number of orders"),
):
    """
    Calculate all PPC metrics

    Example:
        amazon-ppc metrics calculate \\
            --ad-spend 500 \\
            --ad-sales 2000 \\
            --total-sales 5000 \\
            --impressions 10000 \\
            --clicks 100 \\
            --orders 10
    """
    # Calculate metrics
    result = MetricsCalculator.calculate(
        ad_spend=ad_spend,
        ad_sales=ad_sales,
        total_sales=total_sales,
        impressions=impressions,
        clicks=clicks,
        orders=orders,
    )

    # Create results table
    table = Table(title="📊 PPC Metrics Results", show_header=True)
    table.add_column("Metric", style="cyan", width=20)
    table.add_column("Value", style="green", justify="right")
    table.add_column("Benchmark", style="yellow")

    # Add rows
    if result.acos is not None:
        benchmark = _get_acos_benchmark(float(result.acos))
        table.add_row(
            "ACoS",
            f"{result.acos:.2f}%",
            benchmark,
        )

    if result.tacos is not None:
        benchmark = _get_tacos_benchmark(float(result.tacos))
        table.add_row(
            "TACOS",
            f"{result.tacos:.2f}%",
            benchmark,
        )

    if result.roas is not None:
        table.add_row(
            "ROAS",
            f"{result.roas:.2f}x",
            "Higher is better",
        )

    if result.ctr is not None:
        benchmark = _get_ctr_benchmark(float(result.ctr))
        table.add_row(
            "CTR",
            f"{result.ctr:.3f}%",
            benchmark,
        )

    if result.cvr is not None:
        benchmark = _get_cvr_benchmark(float(result.cvr))
        table.add_row(
            "CVR",
            f"{result.cvr:.2f}%",
            benchmark,
        )

    if result.rpc is not None:
        table.add_row(
            "RPC",
            f"${result.rpc:.2f}",
            "Revenue per click",
        )

    if result.cpc is not None:
        table.add_row(
            "CPC",
            f"${result.cpc:.2f}",
            "Cost per click",
        )

    console.print(table)

    # Performance summary
    _print_performance_summary(result)


@app.command()
def acos(
    ad_spend: float = typer.Argument(..., help="Advertising spend"),
    ad_sales: float = typer.Argument(..., help="Sales from ads"),
):
    """
    Calculate ACoS (Advertising Cost of Sale)

    Example:
        amazon-ppc metrics acos 500 2000
    """
    result = MetricsCalculator.calculate_acos(ad_spend, ad_sales)

    console.print(f"\n[bold]ACoS:[/bold] [green]{result:.2f}%[/green]")
    console.print(f"Benchmark: {_get_acos_benchmark(result)}\n")


@app.command()
def tacos(
    ad_spend: float = typer.Argument(..., help="Advertising spend"),
    total_sales: float = typer.Argument(..., help="Total sales"),
):
    """
    Calculate TACOS (Total Advertising Cost of Sale)

    Example:
        amazon-ppc metrics tacos 500 5000
    """
    result = MetricsCalculator.calculate_tacos(ad_spend, total_sales)

    console.print(f"\n[bold]TACOS:[/bold] [green]{result:.2f}%[/green]")
    console.print(f"Benchmark: {_get_tacos_benchmark(result)}\n")


def _get_acos_benchmark(acos: float) -> str:
    """Get ACoS benchmark description"""
    if acos > 50:
        return "❌ Poor - Unprofitable"
    elif acos > 35:
        return "⚠️  High - Above average"
    elif acos > 20:
        return "✓ Average"
    elif acos > 15:
        return "✓✓ Good"
    else:
        return "✓✓✓ Excellent"


def _get_tacos_benchmark(tacos: float) -> str:
    """Get TACOS benchmark description"""
    if tacos < 5:
        return "⚠️  Insufficient - Under-investing"
    elif tacos < 8:
        return "✓ Conservative"
    elif tacos < 12:
        return "✓✓ Standard - Healthy"
    elif tacos < 20:
        return "⚠️  Aggressive"
    else:
        return "⚠️  Ultra Aggressive"


def _get_ctr_benchmark(ctr: float) -> str:
    """Get CTR benchmark description"""
    if ctr < 0.3:
        return "❌ Poor"
    elif ctr < 0.5:
        return "✓ Average"
    elif ctr < 0.75:
        return "✓✓ Good"
    elif ctr < 1.0:
        return "✓✓✓ Very Good"
    else:
        return "⭐ Excellent"


def _get_cvr_benchmark(cvr: float) -> str:
    """Get CVR benchmark description"""
    if cvr < 5:
        return "❌ Poor"
    elif cvr < 10:
        return "✓ Average"
    elif cvr < 15:
        return "✓✓ Good"
    elif cvr < 20:
        return "✓✓✓ Very Good"
    else:
        return "⭐ Excellent"


def _print_performance_summary(result):
    """Print performance summary panel"""
    summary_lines = []

    # Organic to PPC ratio
    organic_sales = float(result.total_sales - result.ad_sales)
    ppc_sales = float(result.ad_sales)

    if ppc_sales > 0:
        ratio = organic_sales / ppc_sales
        summary_lines.append(f"Organic:PPC Ratio: {ratio:.1f}:1")

        if ratio >= 3:
            summary_lines.append("✓✓✓ Excellent - Sustainable")
        elif ratio >= 2:
            summary_lines.append("✓✓ Healthy")
        elif ratio >= 1:
            summary_lines.append("✓ Normal growth")
        else:
            summary_lines.append("⚠️  PPC-dependent")

    console.print(
        Panel(
            "\n".join(summary_lines),
            title="Performance Summary",
            border_style="blue",
        )
    )
