"""
Triangulation Analyzer

Cross-validates data from multiple sources (Helium 10, SellerSprite, Keepa).
Implements the "best practice" of never relying on a single data source.
"""

import logging
from typing import Optional, Any
from statistics import mean, stdev
from ..core.models import AnalysisRule, DecisionStatus, ProductData
from ..api import Helium10Client, SellerSpriteClient, KeepaClient

logger = logging.getLogger(__name__)


class TriangulationAnalyzer:
    """
    Cross-validates data from multiple API sources.

    Research basis:
    - Each tool has different data sources and algorithms
    - Amazon doesn't share official data (except ABA)
    - Single-source reliance is risky
    - Triangulation = industry best practice

    Validation matrix:
    - Sales estimate: Xray vs Market Analysis vs BSR Drops
    - Keyword volume: Magnet/Cerebro vs SellerSprite ABA
    - Competition: Title Density vs Click Concentration vs Seller Count
    - Price trends: N/A vs N/A vs Keepa History
    """

    def __init__(
        self,
        h10_client: Optional[Helium10Client] = None,
        ss_client: Optional[SellerSpriteClient] = None,
        keepa_client: Optional[KeepaClient] = None,
        variance_threshold: float = 0.30,  # 30% variance = yellow flag
    ):
        """
        Initialize triangulation analyzer.

        Args:
            h10_client: Helium 10 API client
            ss_client: SellerSprite API client
            keepa_client: Keepa API client
            variance_threshold: Maximum acceptable variance between sources
        """
        self.h10_client = h10_client
        self.ss_client = ss_client
        self.keepa_client = keepa_client
        self.variance_threshold = variance_threshold

    def analyze(
        self, product: ProductData, keyword: str, marketplace: str = "US"
    ) -> AnalysisRule:
        """
        Perform comprehensive data triangulation.

        Args:
            product: Product data
            keyword: Target keyword
            marketplace: Amazon marketplace

        Returns:
            AnalysisRule: Triangulation analysis result
        """
        logger.info(
            f"Starting triangulation analysis for {product.asin} / {keyword}"
        )

        # Collect data from all sources
        sales_data = self._triangulate_sales(product, marketplace)
        volume_data = self._triangulate_keyword_volume(keyword, marketplace)
        competition_data = self._triangulate_competition(keyword, marketplace)

        # Calculate overall confidence
        confidence_scores = []
        issues = []

        # Sales triangulation confidence
        if sales_data["source_count"] >= 2:
            if sales_data["variance_pct"] <= self.variance_threshold:
                confidence_scores.append(100)
            elif sales_data["variance_pct"] <= self.variance_threshold * 2:
                confidence_scores.append(70)
                issues.append(
                    f"Moderate sales estimate variance: {sales_data['variance_pct']:.1%}"
                )
            else:
                confidence_scores.append(30)
                issues.append(
                    f"High sales estimate variance: {sales_data['variance_pct']:.1%}"
                )
        elif sales_data["source_count"] == 1:
            confidence_scores.append(50)
            issues.append("Only one data source for sales estimates")

        # Keyword volume triangulation confidence
        if volume_data["source_count"] >= 2:
            if volume_data["variance_pct"] <= self.variance_threshold:
                confidence_scores.append(100)
            elif volume_data["variance_pct"] <= self.variance_threshold * 2:
                confidence_scores.append(70)
                issues.append(
                    f"Moderate keyword volume variance: {volume_data['variance_pct']:.1%}"
                )
            else:
                confidence_scores.append(30)
                issues.append(
                    f"High keyword volume variance: {volume_data['variance_pct']:.1%}"
                )
        elif volume_data["source_count"] == 1:
            confidence_scores.append(50)
            issues.append("Only one data source for keyword volume")

        # Overall confidence score
        overall_confidence = mean(confidence_scores) if confidence_scores else 0

        # Determine status
        if overall_confidence >= 80:
            status = DecisionStatus.GREEN
            reason = (
                f"Data triangulation successful with {overall_confidence:.0f}% confidence. "
                f"Cross-validation from {sales_data['source_count']} sources for sales "
                f"and {volume_data['source_count']} sources for keywords. "
                f"Data consistency verified."
            )
        elif overall_confidence >= 60:
            status = DecisionStatus.YELLOW
            reason = (
                f"Moderate data confidence ({overall_confidence:.0f}%). "
                f"Some variance detected between sources: {', '.join(issues)}. "
                f"Proceed with caution and manual verification."
            )
        else:
            status = DecisionStatus.RED
            reason = (
                f"Low data confidence ({overall_confidence:.0f}%). "
                f"Significant discrepancies: {', '.join(issues)}. "
                f"Data reliability questionable. Recommend additional research."
            )

        return AnalysisRule(
            rule_name="triangulation",
            status=status,
            score=overall_confidence,
            reason=reason,
            threshold_value=self.variance_threshold,
            actual_value=overall_confidence / 100,
            metadata={
                "sales_triangulation": sales_data,
                "volume_triangulation": volume_data,
                "competition_triangulation": competition_data,
                "issues": issues,
            },
        )

    def _triangulate_sales(
        self, product: ProductData, marketplace: str
    ) -> dict[str, Any]:
        """Triangulate monthly sales estimates."""
        estimates = {}

        # Helium 10 Xray
        if product.h10_monthly_sales:
            estimates["helium10"] = product.h10_monthly_sales

        # SellerSprite Market Analysis (if available in product data)
        if hasattr(product, "ss_monthly_sales") and product.ss_monthly_sales:
            estimates["sellersprite"] = product.ss_monthly_sales

        # Keepa BSR Drops (approximate)
        if product.keepa_bsr_drops_30d:
            # BSR drops ≈ sales (rough estimate)
            estimates["keepa"] = product.keepa_bsr_drops_30d

        if not estimates:
            return {
                "source_count": 0,
                "estimates": {},
                "mean": 0,
                "variance_pct": 0,
            }

        values = list(estimates.values())
        mean_val = mean(values)
        variance = (max(values) - min(values)) / mean_val if mean_val > 0 else 0

        return {
            "source_count": len(estimates),
            "estimates": estimates,
            "mean": int(mean_val),
            "variance_pct": variance,
            "std_dev": stdev(values) if len(values) > 1 else 0,
        }

    def _triangulate_keyword_volume(
        self, keyword: str, marketplace: str
    ) -> dict[str, Any]:
        """Triangulate keyword search volumes."""
        volumes = {}

        # Helium 10
        if self.h10_client:
            h10_data = self.h10_client.get_keyword_data(keyword, marketplace)
            if h10_data.get("search_volume"):
                volumes["helium10"] = h10_data["search_volume"]

        # SellerSprite (with ABA data)
        if self.ss_client:
            ss_volume = self.ss_client.get_search_volume(keyword, marketplace)
            if ss_volume:
                volumes["sellersprite"] = ss_volume

        if not volumes:
            return {
                "source_count": 0,
                "volumes": {},
                "mean": 0,
                "variance_pct": 0,
            }

        values = list(volumes.values())
        mean_val = mean(values)
        variance = (max(values) - min(values)) / mean_val if mean_val > 0 else 0

        return {
            "source_count": len(volumes),
            "volumes": volumes,
            "mean": int(mean_val),
            "variance_pct": variance,
            "std_dev": stdev(values) if len(values) > 1 else 0,
        }

    def _triangulate_competition(
        self, keyword: str, marketplace: str
    ) -> dict[str, Any]:
        """Triangulate competition metrics."""
        metrics = {}

        # Helium 10 Title Density
        if self.h10_client:
            title_density = self.h10_client.get_title_density(keyword, marketplace)
            if title_density is not None:
                metrics["title_density"] = title_density

        # SellerSprite Click Concentration
        if self.ss_client:
            click_conc = self.ss_client.get_click_concentration(keyword, marketplace)
            if click_conc is not None:
                metrics["click_concentration"] = click_conc

        return {
            "source_count": len(metrics),
            "metrics": metrics,
            "competition_level": self._assess_competition_level(metrics),
        }

    def _assess_competition_level(self, metrics: dict) -> str:
        """Assess overall competition level from metrics."""
        if not metrics:
            return "unknown"

        # Title density: <5 = low, 5-7 = medium, >7 = high
        # Click concentration: <40% = low, 40-60% = medium, >60% = high

        scores = []

        td = metrics.get("title_density")
        if td is not None:
            if td < 5:
                scores.append(1)  # Low
            elif td < 7:
                scores.append(2)  # Medium
            else:
                scores.append(3)  # High

        cc = metrics.get("click_concentration")
        if cc is not None:
            if cc < 0.4:
                scores.append(1)
            elif cc < 0.6:
                scores.append(2)
            else:
                scores.append(3)

        if not scores:
            return "unknown"

        avg_score = mean(scores)
        if avg_score < 1.5:
            return "low"
        elif avg_score < 2.5:
            return "medium"
        else:
            return "high"
