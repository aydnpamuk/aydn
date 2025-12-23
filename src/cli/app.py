"""
Amazon PPC CLI Application

Main entry point for command-line interface
"""

import typer
from rich.console import Console
from rich.table import Table

from .commands import metrics, crisis

app = typer.Typer(
    name="amazon-ppc",
    help="Amazon PPC & SEO Management System - Professional CLI",
    add_completion=False,
)

# Register sub-commands
app.add_typer(metrics.app, name="metrics")
app.add_typer(crisis.app, name="crisis")

console = Console()


@app.command()
def version():
    """Show version information"""
    console.print("[bold green]Amazon PPC System v1.0.0[/bold green]")
    console.print("Based on Amazon PPC & SEO Bible v3.0")
    console.print("Rating: ⭐ 9.5/10")


@app.command()
def info():
    """Show system information and capabilities"""
    table = Table(title="System Capabilities")

    table.add_column("Module", style="cyan", no_wrap=True)
    table.add_column("Features", style="magenta")

    table.add_row(
        "Core Metrics",
        "ACoS, TACOS, CTR, CVR, RPC, ROAS calculations",
    )
    table.add_row(
        "Benchmarks",
        "Industry standards for performance evaluation",
    )
    table.add_row(
        "Bid Optimization",
        "RPC-based bid calculation, placement modifiers",
    )
    table.add_row(
        "Decision Trees",
        "Automated ACoS, CTR, BSR optimization decisions",
    )
    table.add_row(
        "Crisis Management",
        "Stockout, listing, review crisis protocols",
    )
    table.add_row(
        "Golden Rules",
        "5 unbreakable rules compliance checking",
    )

    console.print(table)


if __name__ == "__main__":
    app()
