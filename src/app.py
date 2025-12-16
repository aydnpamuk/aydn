"""
Amazon Private Label Product Analyzer - Main CLI Application

Implements the analysis framework from the research report for evaluating
private label opportunities on Amazon.
"""

import sys
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from .core.config import settings
from .core.models import ProductData, KeywordData, Marketplace, DecisionStatus
from .api import Helium10Client, SellerSpriteClient, KeepaClient
from .decision import ScoringEngine
from .reports import JSONReporter, CSVReporter
from .utils.logger import setup_logger

# Setup
console = Console()
logger = setup_logger(level=settings.log_level, log_file=settings.log_file)


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """
    Amazon Private Label Product Analyzer

    Analyzes products using data-driven rules from industry research:
    - Price Barrier ($39+ rule)
    - Brand Dominance (50% monopoly check)
    - Keyword Volume (3,000+ searches)
    - Triangulation (cross-validation)
    - Final decision: RED/YELLOW/GREEN
    """
    pass


@cli.command()
@click.argument("asin")
@click.argument("keyword")
@click.option(
    "--marketplace",
    "-m",
    type=click.Choice(["US", "UK", "DE", "FR", "IT", "ES", "CA", "JP"]),
    default="US",
    help="Amazon marketplace",
)
@click.option(
    "--output-format",
    "-f",
    type=click.Choice(["json", "csv", "both", "none"]),
    default="json",
    help="Report output format",
)
@click.option("--output-dir", "-o", default=None, help="Output directory for reports")
def analyze(asin: str, keyword: str, marketplace: str, output_format: str, output_dir: str):
    """
    Analyze a product by ASIN and target keyword.

    Example:
        aydn analyze B08N5WRWNW "hydraulic crimper" -m US -f json
    """
    console.print(Panel.fit(
        "[bold blue]Amazon Private Label Product Analyzer[/bold blue]\n"
        f"ASIN: {asin} | Keyword: {keyword} | Marketplace: {marketplace}",
        border_style="blue"
    ))

    # Validate API keys
    api_status = settings.validate_api_keys()
    missing_keys = [k for k, v in api_status.items() if not v]

    if missing_keys:
        console.print(
            f"[yellow]Warning: Missing API keys: {', '.join(missing_keys)}[/yellow]"
        )
        console.print("Set API keys in .env file. Analysis will use available data only.")
        console.print()

    # Initialize API clients
    h10_client = None
    ss_client = None
    keepa_client = None

    try:
        if api_status["helium10"]:
            h10_client = Helium10Client(
                api_key=settings.api_config.helium10_api_key,
                base_url=settings.api_config.helium10_base_url,
                timeout=settings.api_config.timeout,
            )

        if api_status["sellersprite"]:
            ss_client = SellerSpriteClient(
                api_key=settings.api_config.sellersprite_api_key,
                base_url=settings.api_config.sellersprite_base_url,
                timeout=settings.api_config.timeout,
            )

        if api_status["keepa"]:
            keepa_client = KeepaClient(
                api_key=settings.api_config.keepa_api_key,
                base_url=settings.api_config.keepa_base_url,
                timeout=settings.api_config.timeout,
            )

    except Exception as e:
        console.print(f"[red]Error initializing API clients: {e}[/red]")
        sys.exit(1)

    # Fetch product data
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Fetch from APIs
        task1 = progress.add_task("Fetching product data...", total=None)
        product_data = _fetch_product_data(
            asin, marketplace, h10_client, ss_client, keepa_client
        )
        progress.update(task1, completed=True)

        task2 = progress.add_task("Fetching keyword data...", total=None)
        keyword_data = _fetch_keyword_data(
            keyword, marketplace, h10_client, ss_client
        )
        progress.update(task2, completed=True)

        task3 = progress.add_task("Running analysis...", total=None)
        engine = ScoringEngine(
            h10_client=h10_client,
            ss_client=ss_client,
            keepa_client=keepa_client,
        )
        result = engine.analyze_product(product_data, keyword, keyword_data)
        progress.update(task3, completed=True)

    # Display results
    _display_results(result)

    # Generate reports
    if output_format != "none":
        output_path = output_dir or settings.output_dir
        _generate_reports(result, output_format, output_path)

    # Exit code based on decision
    if result.final_decision == DecisionStatus.GREEN:
        sys.exit(0)
    elif result.final_decision == DecisionStatus.YELLOW:
        sys.exit(1)
    else:
        sys.exit(2)


@cli.command()
def validate():
    """Validate API configuration and test connections."""
    console.print("[bold]Validating API Configuration[/bold]\n")

    api_status = settings.validate_api_keys()

    table = Table(title="API Status")
    table.add_column("Service", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Endpoint", style="dim")

    for service, is_valid in api_status.items():
        status = "✓ Configured" if is_valid else "✗ Missing"
        status_style = "green" if is_valid else "red"

        if service == "helium10":
            endpoint = settings.api_config.helium10_base_url
        elif service == "sellersprite":
            endpoint = settings.api_config.sellersprite_base_url
        elif service == "keepa":
            endpoint = settings.api_config.keepa_base_url
        else:
            endpoint = "N/A"

        table.add_row(service.title(), f"[{status_style}]{status}[/{status_style}]", endpoint)

    console.print(table)
    console.print()

    if all(api_status.values()):
        console.print("[green]✓ All API keys configured![/green]")
    else:
        console.print("[yellow]⚠ Some API keys missing. Set them in .env file.[/yellow]")


@cli.command()
@click.argument("keyword")
@click.option("--marketplace", "-m", default="US", help="Amazon marketplace")
@click.option("--min-price", type=float, default=None, help="Minimum price filter")
@click.option("--max-price", type=float, default=None, help="Maximum price filter")
@click.option("--limit", "-l", type=int, default=10, help="Number of products to analyze")
def discover(keyword: str, marketplace: str, min_price: float, max_price: float, limit: int):
    """
    Discover and analyze products by keyword.

    Uses Black Box to find products matching criteria.

    Example:
        aydn discover "yoga mat" --min-price 39 --limit 20
    """
    console.print(f"[bold]Product Discovery: {keyword}[/bold]\n")
    console.print("[yellow]Feature coming soon: Black Box integration[/yellow]")


def _fetch_product_data(
    asin: str,
    marketplace: str,
    h10_client,
    ss_client,
    keepa_client,
) -> ProductData:
    """Fetch product data from all available sources."""
    # Start with basic data
    product = ProductData(
        asin=asin,
        title=f"Product {asin}",  # Would fetch from API
        price=0.0,
        marketplace=Marketplace[marketplace],
    )

    # Fetch from Helium 10
    if h10_client:
        try:
            h10_data = h10_client.get_product_data(asin, marketplace)
            product.price = h10_data.get("price", 0.0)
            product.title = h10_data.get("title", product.title)
            product.h10_monthly_revenue = h10_data.get("monthly_revenue")
            product.h10_monthly_sales = h10_data.get("monthly_sales")
            product.h10_review_count = h10_data.get("review_count")
            product.h10_rating = h10_data.get("rating")
        except Exception as e:
            logger.error(f"Helium 10 fetch failed: {e}")

    # Fetch from SellerSprite
    if ss_client:
        try:
            ss_traffic = ss_client.get_traffic_analysis(asin, marketplace)
            product.ss_organic_traffic_ratio = ss_traffic.get("organic_ratio")
            product.ss_sponsored_traffic_ratio = ss_traffic.get("sponsored_ratio")
        except Exception as e:
            logger.error(f"SellerSprite fetch failed: {e}")

    # Fetch from Keepa
    if keepa_client:
        try:
            domain = 1 if marketplace == "US" else 2  # Simplified
            keepa_data = keepa_client.get_product(asin, domain=domain)

            if keepa_data.get("products"):
                prod = keepa_data["products"][0]
                product.keepa_sales_rank = prod.get("salesRank")
                product.keepa_seller_count = prod.get("offersCount")

            # Get price averages
            product.keepa_avg_price_30d = keepa_client.get_average_price(
                asin, domain=domain, days=30
            )
            product.keepa_bsr_drops_30d = keepa_client.get_sales_rank_drops(
                asin, domain=domain, days=30
            )
        except Exception as e:
            logger.error(f"Keepa fetch failed: {e}")

    # Set default price if still 0
    if product.price == 0.0:
        console.print("[yellow]Warning: Could not fetch product price. Using default $45[/yellow]")
        product.price = 45.0

    return product


def _fetch_keyword_data(
    keyword: str,
    marketplace: str,
    h10_client,
    ss_client,
) -> KeywordData:
    """Fetch keyword data from available sources."""
    volume = 0

    # Try Helium 10
    if h10_client:
        try:
            h10_kw = h10_client.get_keyword_data(keyword, marketplace)
            volume = h10_kw.get("search_volume", 0)
        except Exception as e:
            logger.error(f"Helium 10 keyword fetch failed: {e}")

    # Try SellerSprite if H10 failed
    if volume == 0 and ss_client:
        try:
            volume = ss_client.get_search_volume(keyword, marketplace) or 0
        except Exception as e:
            logger.error(f"SellerSprite keyword fetch failed: {e}")

    # Default if no data
    if volume == 0:
        console.print(f"[yellow]Warning: Could not fetch search volume for '{keyword}'. Using default 5000[/yellow]")
        volume = 5000

    return KeywordData(keyword=keyword, exact_search_volume=volume)


def _display_results(result):
    """Display analysis results in terminal."""
    # Decision panel
    decision_color = {
        DecisionStatus.GREEN: "green",
        DecisionStatus.YELLOW: "yellow",
        DecisionStatus.RED: "red",
    }[result.final_decision]

    decision_emoji = {
        DecisionStatus.GREEN: "✅",
        DecisionStatus.YELLOW: "⚠️",
        DecisionStatus.RED: "❌",
    }[result.final_decision]

    console.print()
    console.print(Panel(
        f"[bold {decision_color}]{decision_emoji} {result.final_decision.value}[/bold {decision_color}]\n\n"
        f"Overall Score: {result.overall_score:.1f}/100\n\n"
        f"{result.recommendation}",
        title="Analysis Result",
        border_style=decision_color,
    ))

    # Detailed scores table
    table = Table(title="\nDetailed Analysis")
    table.add_column("Rule", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("Score", justify="right")
    table.add_column("Details")

    def add_rule(name, rule):
        if rule:
            status_icon = {
                DecisionStatus.GREEN: "✓",
                DecisionStatus.YELLOW: "⚠",
                DecisionStatus.RED: "✗",
            }[rule.status]
            status_color = {
                DecisionStatus.GREEN: "green",
                DecisionStatus.YELLOW: "yellow",
                DecisionStatus.RED: "red",
            }[rule.status]
            table.add_row(
                name,
                f"[{status_color}]{status_icon}[/{status_color}]",
                f"{rule.score:.1f}",
                f"T:{rule.threshold_value} | A:{rule.actual_value}",
            )

    add_rule("Price Barrier", result.price_barrier_check)
    add_rule("Brand Dominance", result.brand_dominance_check)
    add_rule("Keyword Volume", result.keyword_volume_check)
    if result.triangulation_check:
        add_rule("Triangulation", result.triangulation_check)

    console.print(table)

    # Risk factors
    if result.risk_factors:
        console.print("\n[bold red]⚠ Risk Factors:[/bold red]")
        for risk in result.risk_factors:
            console.print(f"  • {risk}")

    # Opportunities
    if result.opportunity_factors:
        console.print("\n[bold green]✓ Opportunities:[/bold green]")
        for opp in result.opportunity_factors:
            console.print(f"  • {opp}")

    # Next steps
    console.print("\n[bold]Next Steps:[/bold]")
    for i, step in enumerate(result.next_steps, 1):
        console.print(f"  {i}. {step}")

    console.print()


def _generate_reports(result, output_format: str, output_dir: str):
    """Generate analysis reports."""
    try:
        if output_format in ["json", "both"]:
            json_reporter = JSONReporter(output_dir)
            json_path = json_reporter.generate_report(result)
            console.print(f"[green]✓ JSON report: {json_path}[/green]")

        if output_format in ["csv", "both"]:
            csv_reporter = CSVReporter(output_dir)
            csv_path = csv_reporter.generate_report(result)
            console.print(f"[green]✓ CSV report: {csv_path}[/green]")

    except Exception as e:
        console.print(f"[red]Error generating reports: {e}[/red]")


def main():
    """Main entry point."""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        logger.exception("Unhandled exception")
        sys.exit(1)


if __name__ == "__main__":
    main()
