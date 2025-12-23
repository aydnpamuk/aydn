"""
Crisis Management CLI Commands

Commands for handling emergency situations
"""

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from datetime import datetime

from ...crisis.stockout.protocol import StockoutProtocol, StockLevel

app = typer.Typer(help="Crisis management protocols")
console = Console()


@app.command()
def stockout(
    current_stock: int = typer.Option(..., help="Current stock units"),
    daily_velocity: float = typer.Option(..., help="Average daily sales"),
    lead_time: int = typer.Option(30, help="Reorder lead time in days"),
):
    """
    Analyze stock situation and get crisis protocol

    Example:
        amazon-ppc crisis stockout --current-stock 100 --daily-velocity 5.0 --lead-time 30
    """
    console.print("\n[bold]🚨 Stock Crisis Analysis[/bold]\n")

    # Analyze stock
    analysis = StockoutProtocol.analyze_stock_situation(
        current_stock=current_stock,
        daily_velocity=daily_velocity,
        lead_time_days=lead_time,
    )

    # Display stock status
    _display_stock_status(analysis)

    # Display recommended actions
    _display_actions(analysis)

    # Display reorder point
    reorder_point = StockoutProtocol.calculate_reorder_point(
        daily_velocity=daily_velocity,
        lead_time_days=lead_time,
    )

    console.print(
        Panel(
            f"[bold]Reorder Point:[/bold] {reorder_point} units\n"
            f"Place next order when stock reaches this level",
            title="📋 Reorder Planning",
            border_style="blue",
        )
    )


@app.command()
def check_stock(
    current_stock: int = typer.Argument(..., help="Current stock units"),
    daily_velocity: float = typer.Argument(..., help="Daily sales"),
):
    """
    Quick stock check

    Example:
        amazon-ppc crisis check-stock 100 5.0
    """
    days_remaining = current_stock / daily_velocity if daily_velocity > 0 else float("inf")

    console.print(f"\n[bold]Stock Status:[/bold]")
    console.print(f"Current Stock: {current_stock} units")
    console.print(f"Daily Velocity: {daily_velocity:.1f} units/day")
    console.print(f"Days Remaining: [yellow]{days_remaining:.1f} days[/yellow]")

    # Status indicator
    if days_remaining < 7:
        console.print("[red]⚠️  CRITICAL - Immediate action required[/red]")
    elif days_remaining < 14:
        console.print("[yellow]⚠️  WARNING - Place order soon[/yellow]")
    elif days_remaining < 28:
        console.print("[blue]ℹ️  NOTICE - Below safety threshold[/blue]")
    else:
        console.print("[green]✓ HEALTHY - Stock levels good[/green]")

    # PPC recommendation
    should_pause = StockoutProtocol.should_pause_ppc(days_remaining)
    budget_multiplier = StockoutProtocol.calculate_budget_reduction(days_remaining)

    console.print(f"\n[bold]PPC Recommendation:[/bold]")
    if should_pause:
        console.print("[red]PAUSE all PPC campaigns[/red]")
    elif budget_multiplier < 1.0:
        reduction_pct = (1 - budget_multiplier) * 100
        console.print(f"[yellow]Reduce PPC budget by {reduction_pct:.0f}%[/yellow]")
    else:
        console.print("[green]Continue normal PPC operations[/green]")

    console.print()


def _display_stock_status(analysis):
    """Display stock status information"""
    # Status color
    if analysis.stock_level == StockLevel.EMERGENCY:
        status_color = "red"
        status_icon = "🔴"
    elif analysis.stock_level == StockLevel.CRITICAL:
        status_color = "yellow"
        status_icon = "🟡"
    elif analysis.stock_level == StockLevel.WARNING:
        status_color = "blue"
        status_icon = "🔵"
    else:
        status_color = "green"
        status_icon = "🟢"

    # Create status table
    table = Table(title=f"{status_icon} Stock Status")
    table.add_column("Item", style="cyan")
    table.add_column("Value", style=status_color, justify="right")

    table.add_row("Current Stock", f"{analysis.current_stock} units")
    table.add_row("Daily Velocity", f"{analysis.daily_velocity:.1f} units/day")
    table.add_row("Days Remaining", f"{analysis.days_remaining:.1f} days")
    table.add_row("Status", analysis.stock_level.value.upper())

    if analysis.estimated_stockout_date:
        table.add_row(
            "Estimated Stockout",
            analysis.estimated_stockout_date.strftime("%Y-%m-%d"),
        )

    console.print(table)
    console.print()


def _display_actions(analysis):
    """Display recommended actions"""
    if not analysis.recommended_actions:
        return

    console.print("[bold]📋 Recommended Actions[/bold]\n")

    for idx, action in enumerate(analysis.recommended_actions, 1):
        # Priority color
        if action.priority.value == "immediate":
            priority_color = "red"
            priority_icon = "🔴"
        elif action.priority.value == "short_term":
            priority_color = "yellow"
            priority_icon = "🟡"
        else:
            priority_color = "blue"
            priority_icon = "🔵"

        console.print(
            f"{priority_icon} [bold {priority_color}]{action.priority.value.upper()}[/bold {priority_color}]"
        )
        console.print(f"   Action: {action.action}")
        console.print(f"   Reason: {action.reason}")

        if action.deadline:
            console.print(f"   Deadline: {action.deadline.strftime('%Y-%m-%d %H:%M')}")

        console.print()
