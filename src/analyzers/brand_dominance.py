"""
Brand Dominance Analyzer

Implements the 50% market monopoly rule from the research report.
Markets dominated by a single brand or Amazon are typically rejected.
"""

import logging
from typing import Optional, Any
from ..core.models import AnalysisRule, DecisionStatus, ProductData
from ..core.config import settings
from ..api import SellerSpriteClient, KeepaClient

logger = logging.getLogger(__name__)


class BrandDominanceAnalyzer:
    """
    Analyzes market dominance and monopoly risk.

    Research basis:
    - Click Concentration >60% = high monopoly
    - Amazon's private label threat (400+ brands)
    - FTC investigation: Amazon uses seller data for own products
    - Top 3 products taking 70%+ clicks = locked market
    """

    def __init__(
        self,
        dominance_threshold: Optional[float] = None,
        ss_client: Optional[SellerSpriteClient] = None,
        keepa_client: Optional[KeepaClient] = None,
    ):
        """
        Initialize brand dominance analyzer.

        Args:
            dominance_threshold: Maximum allowed market share (default from config)
            ss_client: SellerSprite API client
            keepa_client: Keepa API client
        """
        self.dominance_threshold = (
            dominance_threshold or settings.brand_dominance_threshold
        )
        self.ss_client = ss_client
        self.keepa_client = keepa_client

    def analyze(
        self, product: ProductData, keyword: str, marketplace: str = "US"
    ) -> AnalysisRule:
        """
        Analyze market dominance for the product's niche.

        Args:
            product: Product data
            keyword: Target keyword/niche
            marketplace: Amazon marketplace

        Returns:
            AnalysisRule: Analysis result
        """
        logger.info(
            f"Analyzing brand dominance for keyword: {keyword}, "
            f"marketplace: {marketplace}"
        )

        # Get click concentration from SellerSprite
        click_concentration = None
        if self.ss_client:
            click_concentration = self.ss_client.get_click_concentration(
                keyword, marketplace
            )

        # Get top competitors to check for Amazon dominance
        amazon_detected = False
        top_brand_share = None

        if self.ss_client:
            competitors = self.ss_client.get_top_competitors(keyword, marketplace)
            if competitors:
                # Check if Amazon is in top 3
                for i, comp in enumerate(competitors[:3]):
                    brand = comp.get("brand", "").lower()
                    if "amazon" in brand or brand in [
                        "basics",
                        "essentials",
                        "solimo",
                    ]:
                        amazon_detected = True
                        break

                # Calculate top brand share if data available
                if len(competitors) > 0:
                    top_brand = competitors[0].get("brand")
                    same_brand_count = sum(
                        1 for c in competitors[:10] if c.get("brand") == top_brand
                    )
                    top_brand_share = same_brand_count / len(competitors[:10])

        # Use click concentration as primary metric
        dominance_score = click_concentration or top_brand_share or 0.0

        logger.info(
            f"Dominance metrics - Click concentration: {click_concentration}, "
            f"Amazon detected: {amazon_detected}, "
            f"Top brand share: {top_brand_share}"
        )

        # Scoring and decision
        if amazon_detected:
            score = 0.0
            status = DecisionStatus.RED
            reason = (
                "🚨 CRITICAL: Amazon's private label detected in top positions. "
                "High risk of direct competition from Amazon. "
                "Amazon has 400+ brands and uses seller data for product development. "
                "AVOID this niche."
            )

        elif dominance_score >= 0.70:
            score = 10.0
            status = DecisionStatus.RED
            reason = (
                f"Market is highly monopolized ({dominance_score:.1%} concentration). "
                f"Top 3 products dominate 70%+ of traffic. "
                f"Extremely difficult to break in. High PPC costs expected."
            )

        elif dominance_score >= self.dominance_threshold:
            score = 30.0
            status = DecisionStatus.YELLOW
            reason = (
                f"Moderate market monopoly detected ({dominance_score:.1%} concentration). "
                f"Significant competition from established brands. "
                f"Consider only with strong differentiation strategy."
            )

        elif dominance_score >= 0.40:
            score = 60.0
            status = DecisionStatus.YELLOW
            reason = (
                f"Market has some concentration ({dominance_score:.1%}). "
                f"Competitive but penetrable with good product differentiation. "
                f"Monitor closely for Amazon's entry."
            )

        else:
            score = 90.0
            status = DecisionStatus.GREEN
            reason = (
                f"Low market concentration ({dominance_score:.1%}). "
                f"Fragmented market with no dominant player. "
                f"Good opportunity for new entrants with quality product."
            )

        return AnalysisRule(
            rule_name="brand_dominance",
            status=status,
            score=score,
            reason=reason,
            threshold_value=self.dominance_threshold,
            actual_value=dominance_score,
            metadata={
                "click_concentration": click_concentration,
                "amazon_detected": amazon_detected,
                "top_brand_share": top_brand_share,
                "keyword": keyword,
                "marketplace": marketplace,
            },
        )

    def check_amazon_presence(
        self, keyword: str, marketplace: str = "US"
    ) -> dict[str, Any]:
        """
        Specifically check for Amazon's private label presence.

        Args:
            keyword: Target keyword
            marketplace: Amazon marketplace

        Returns:
            dict: Amazon presence analysis
        """
        if not self.ss_client:
            return {"detected": False, "confidence": 0.0}

        competitors = self.ss_client.get_top_competitors(keyword, marketplace, limit=20)

        amazon_brands = [
            "amazon",
            "amazonbasics",
            "basics",
            "amazon essentials",
            "essentials",
            "solimo",
            "presto!",
            "mama bear",
            "wag",
            "goodthreads",
            "peak velocity",
            "amazon commercial",
        ]

        amazon_products = []
        for comp in competitors:
            brand = comp.get("brand", "").lower()
            if any(ab in brand for ab in amazon_brands):
                amazon_products.append(comp)

        detected = len(amazon_products) > 0
        confidence = len(amazon_products) / len(competitors) if competitors else 0.0

        return {
            "detected": detected,
            "product_count": len(amazon_products),
            "total_competitors": len(competitors),
            "confidence": confidence,
            "amazon_products": amazon_products[:5],  # Top 5
        }
