"""
CSV Report Generator
"""

import csv
import logging
from pathlib import Path
from datetime import datetime
from typing import Union
from ..core.models import ProductAnalysisResult

logger = logging.getLogger(__name__)


class CSVReporter:
    """Generates CSV format reports."""

    def __init__(self, output_dir: Union[str, Path] = "./reports"):
        """
        Initialize CSV reporter.

        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_report(
        self, result: ProductAnalysisResult, filename: str = None
    ) -> Path:
        """
        Generate CSV report for analysis result.

        Args:
            result: Analysis result
            filename: Custom filename (optional)

        Returns:
            Path: Path to generated report
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analysis_{result.asin}_{timestamp}.csv"

        filepath = self.output_dir / filename

        try:
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)

                # Header section
                writer.writerow(["Amazon Private Label Product Analysis"])
                writer.writerow(["Generated", datetime.now().isoformat()])
                writer.writerow(["ASIN", result.asin])
                writer.writerow(["Marketplace", result.marketplace.value])
                writer.writerow([])

                # Summary
                writer.writerow(["SUMMARY"])
                writer.writerow(["Final Decision", result.final_decision.value])
                writer.writerow(["Overall Score", f"{result.overall_score:.2f}/100"])
                writer.writerow(["Recommendation", result.recommendation])
                writer.writerow([])

                # Detailed Analysis
                writer.writerow(["DETAILED ANALYSIS"])
                writer.writerow(
                    ["Rule", "Status", "Score", "Threshold", "Actual", "Reason"]
                )

                self._write_rule_row(writer, "Price Barrier", result.price_barrier_check)
                self._write_rule_row(
                    writer, "Brand Dominance", result.brand_dominance_check
                )
                self._write_rule_row(
                    writer, "Keyword Volume", result.keyword_volume_check
                )

                if result.review_velocity_check:
                    self._write_rule_row(
                        writer, "Review Velocity", result.review_velocity_check
                    )
                if result.title_density_check:
                    self._write_rule_row(
                        writer, "Title Density", result.title_density_check
                    )
                if result.triangulation_check:
                    self._write_rule_row(
                        writer, "Triangulation", result.triangulation_check
                    )

                writer.writerow([])

                # Risk Assessment
                writer.writerow(["RISK ASSESSMENT"])
                writer.writerow(["Risk Factors", len(result.risk_factors)])
                for risk in result.risk_factors:
                    writer.writerow(["", risk])
                writer.writerow([])

                writer.writerow(["Opportunity Factors", len(result.opportunity_factors)])
                for opp in result.opportunity_factors:
                    writer.writerow(["", opp])
                writer.writerow([])

                # Financial Projections
                writer.writerow(["FINANCIAL PROJECTIONS"])
                writer.writerow(
                    ["Est. Monthly Revenue", result.estimated_monthly_revenue or "N/A"]
                )
                writer.writerow(
                    ["Est. Monthly Units", result.estimated_monthly_units or "N/A"]
                )
                writer.writerow(
                    [
                        "Est. Profit Margin",
                        (
                            f"{result.estimated_profit_margin:.1f}%"
                            if result.estimated_profit_margin
                            else "N/A"
                        ),
                    ]
                )
                writer.writerow([])

                # Next Steps
                writer.writerow(["NEXT STEPS"])
                for i, step in enumerate(result.next_steps, 1):
                    writer.writerow([f"{i}.", step])

            logger.info(f"CSV report generated: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Failed to generate CSV report: {e}")
            raise

    def _write_rule_row(self, writer, rule_name: str, rule):
        """Write a rule row to CSV."""
        writer.writerow(
            [
                rule_name,
                rule.status.value,
                f"{rule.score:.2f}",
                rule.threshold_value or "",
                rule.actual_value or "",
                rule.reason,
            ]
        )

    def generate_batch_report(
        self, results: list[ProductAnalysisResult], filename: str = None
    ) -> Path:
        """
        Generate batch report for multiple products in CSV.

        Args:
            results: List of analysis results
            filename: Custom filename (optional)

        Returns:
            Path: Path to generated report
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"batch_analysis_{timestamp}.csv"

        filepath = self.output_dir / filename

        try:
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)

                # Header
                writer.writerow(["Amazon Private Label Batch Analysis"])
                writer.writerow(["Generated", datetime.now().isoformat()])
                writer.writerow(["Total Products", len(results)])
                writer.writerow([])

                # Summary
                green_count = sum(
                    1 for r in results if r.final_decision.value == "GREEN"
                )
                yellow_count = sum(
                    1 for r in results if r.final_decision.value == "YELLOW"
                )
                red_count = sum(1 for r in results if r.final_decision.value == "RED")
                avg_score = (
                    sum(r.overall_score for r in results) / len(results)
                    if results
                    else 0
                )

                writer.writerow(["GREEN", green_count])
                writer.writerow(["YELLOW", yellow_count])
                writer.writerow(["RED", red_count])
                writer.writerow(["Avg Score", f"{avg_score:.2f}"])
                writer.writerow([])

                # Product list
                writer.writerow(
                    [
                        "ASIN",
                        "Decision",
                        "Score",
                        "Price Check",
                        "Brand Check",
                        "Keyword Check",
                        "Est. Revenue",
                        "Est. Margin %",
                    ]
                )

                for result in results:
                    writer.writerow(
                        [
                            result.asin,
                            result.final_decision.value,
                            f"{result.overall_score:.2f}",
                            result.price_barrier_check.status.value,
                            result.brand_dominance_check.status.value,
                            result.keyword_volume_check.status.value,
                            result.estimated_monthly_revenue or "N/A",
                            (
                                f"{result.estimated_profit_margin:.1f}%"
                                if result.estimated_profit_margin
                                else "N/A"
                            ),
                        ]
                    )

            logger.info(f"Batch CSV report generated: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Failed to generate batch CSV report: {e}")
            raise
