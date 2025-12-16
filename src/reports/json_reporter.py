"""
JSON Report Generator
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Union
from ..core.models import ProductAnalysisResult

logger = logging.getLogger(__name__)


class JSONReporter:
    """Generates JSON format reports."""

    def __init__(self, output_dir: Union[str, Path] = "./reports"):
        """
        Initialize JSON reporter.

        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_report(
        self, result: ProductAnalysisResult, filename: str = None
    ) -> Path:
        """
        Generate JSON report for analysis result.

        Args:
            result: Analysis result
            filename: Custom filename (optional)

        Returns:
            Path: Path to generated report
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analysis_{result.asin}_{timestamp}.json"

        filepath = self.output_dir / filename

        # Convert to dict for JSON serialization
        report_data = self._build_report_structure(result)

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)

            logger.info(f"JSON report generated: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Failed to generate JSON report: {e}")
            raise

    def _build_report_structure(self, result: ProductAnalysisResult) -> dict:
        """Build structured report data."""
        return {
            "meta": {
                "report_type": "Amazon Private Label Product Analysis",
                "version": "1.0",
                "generated_at": datetime.now().isoformat(),
                "asin": result.asin,
                "marketplace": result.marketplace.value,
                "analyzed_at": result.analyzed_at.isoformat(),
            },
            "summary": {
                "final_decision": result.final_decision.value,
                "overall_score": round(result.overall_score, 2),
                "recommendation": result.recommendation,
            },
            "detailed_analysis": {
                "price_barrier": self._rule_to_dict(result.price_barrier_check),
                "brand_dominance": self._rule_to_dict(result.brand_dominance_check),
                "keyword_volume": self._rule_to_dict(result.keyword_volume_check),
                "review_velocity": (
                    self._rule_to_dict(result.review_velocity_check)
                    if result.review_velocity_check
                    else None
                ),
                "title_density": (
                    self._rule_to_dict(result.title_density_check)
                    if result.title_density_check
                    else None
                ),
                "click_concentration": (
                    self._rule_to_dict(result.click_concentration_check)
                    if result.click_concentration_check
                    else None
                ),
                "triangulation": (
                    self._rule_to_dict(result.triangulation_check)
                    if result.triangulation_check
                    else None
                ),
            },
            "risk_assessment": {
                "risk_factors": result.risk_factors,
                "risk_count": len(result.risk_factors),
                "opportunity_factors": result.opportunity_factors,
                "opportunity_count": len(result.opportunity_factors),
            },
            "financial_projections": {
                "estimated_monthly_revenue": result.estimated_monthly_revenue,
                "estimated_monthly_units": result.estimated_monthly_units,
                "estimated_profit_margin_pct": result.estimated_profit_margin,
            },
            "action_plan": {
                "next_steps": result.next_steps,
            },
        }

    def _rule_to_dict(self, rule: Union["AnalysisRule", None]) -> dict:
        """Convert AnalysisRule to dict."""
        if rule is None:
            return None

        return {
            "status": rule.status.value,
            "score": round(rule.score, 2),
            "reason": rule.reason,
            "threshold_value": rule.threshold_value,
            "actual_value": rule.actual_value,
            "metadata": rule.metadata,
        }

    def generate_batch_report(
        self, results: list[ProductAnalysisResult], filename: str = None
    ) -> Path:
        """
        Generate batch report for multiple products.

        Args:
            results: List of analysis results
            filename: Custom filename (optional)

        Returns:
            Path: Path to generated report
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"batch_analysis_{timestamp}.json"

        filepath = self.output_dir / filename

        batch_data = {
            "meta": {
                "report_type": "Amazon Private Label Batch Analysis",
                "version": "1.0",
                "generated_at": datetime.now().isoformat(),
                "product_count": len(results),
            },
            "summary": {
                "green_count": sum(
                    1 for r in results if r.final_decision.value == "GREEN"
                ),
                "yellow_count": sum(
                    1 for r in results if r.final_decision.value == "YELLOW"
                ),
                "red_count": sum(
                    1 for r in results if r.final_decision.value == "RED"
                ),
                "avg_score": (
                    sum(r.overall_score for r in results) / len(results)
                    if results
                    else 0
                ),
            },
            "products": [self._build_report_structure(r) for r in results],
        }

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(batch_data, f, indent=2, ensure_ascii=False, default=str)

            logger.info(f"Batch JSON report generated: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Failed to generate batch JSON report: {e}")
            raise
