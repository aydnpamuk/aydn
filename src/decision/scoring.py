"""
Scoring Engine

Combines all analysis rules into final RED/YELLOW/GREEN decision.
"""

import logging
from typing import Optional
from datetime import datetime
from ..core.models import (
    ProductData,
    KeywordData,
    AnalysisRule,
    ProductAnalysisResult,
    DecisionStatus,
    Marketplace,
)
from ..core.config import settings
from ..analyzers import (
    PriceBarrierAnalyzer,
    BrandDominanceAnalyzer,
    KeywordVolumeAnalyzer,
    TriangulationAnalyzer,
)
from ..api import Helium10Client, SellerSpriteClient, KeepaClient

logger = logging.getLogger(__name__)


class ScoringEngine:
    """
    Main scoring engine that orchestrates all analyzers.

    Combines weighted scores from:
    - Price Barrier (25%)
    - Brand Dominance (25%)
    - Keyword Volume (20%)
    - Review Velocity (10%)
    - Title Density (10%)
    - Triangulation (10%)

    Final decision thresholds:
    - >= 70: GREEN (Approve)
    - 40-69: YELLOW (Caution)
    - < 40: RED (Reject)
    """

    def __init__(
        self,
        h10_client: Optional[Helium10Client] = None,
        ss_client: Optional[SellerSpriteClient] = None,
        keepa_client: Optional[KeepaClient] = None,
    ):
        """
        Initialize scoring engine with API clients.

        Args:
            h10_client: Helium 10 API client
            ss_client: SellerSprite API client
            keepa_client: Keepa API client
        """
        self.h10_client = h10_client
        self.ss_client = ss_client
        self.keepa_client = keepa_client

        # Initialize analyzers
        self.price_analyzer = PriceBarrierAnalyzer()
        self.brand_analyzer = BrandDominanceAnalyzer(
            ss_client=ss_client, keepa_client=keepa_client
        )
        self.keyword_analyzer = KeywordVolumeAnalyzer(
            h10_client=h10_client, ss_client=ss_client
        )
        self.triangulation_analyzer = TriangulationAnalyzer(
            h10_client=h10_client, ss_client=ss_client, keepa_client=keepa_client
        )

    def analyze_product(
        self,
        product: ProductData,
        keyword: str,
        keyword_data: Optional[KeywordData] = None,
    ) -> ProductAnalysisResult:
        """
        Perform comprehensive product analysis.

        Args:
            product: Product data
            keyword: Target keyword for the product
            keyword_data: Optional pre-fetched keyword data

        Returns:
            ProductAnalysisResult: Complete analysis with final decision
        """
        logger.info(f"Starting comprehensive analysis for {product.asin}")

        marketplace_str = product.marketplace.value

        # Run all analyzers
        price_check = self.price_analyzer.analyze(product)

        brand_check = self.brand_analyzer.analyze(
            product, keyword, marketplace_str
        )

        # Get or create keyword data
        if keyword_data is None:
            keyword_data = self._fetch_keyword_data(keyword, marketplace_str)

        keyword_check = self.keyword_analyzer.analyze(keyword_data)

        triangulation_check = self.triangulation_analyzer.analyze(
            product, keyword, marketplace_str
        )

        # Optional checks
        review_check = self._analyze_review_velocity(product, marketplace_str)
        title_density_check = self._analyze_title_density(keyword, marketplace_str)
        click_concentration_check = self._analyze_click_concentration(
            keyword, marketplace_str
        )

        # Calculate weighted overall score
        overall_score = self._calculate_weighted_score(
            price_check=price_check,
            brand_check=brand_check,
            keyword_check=keyword_check,
            triangulation_check=triangulation_check,
            review_check=review_check,
            title_density_check=title_density_check,
        )

        # Determine final decision
        final_decision = self._determine_final_decision(
            overall_score,
            price_check,
            brand_check,
            keyword_check,
            triangulation_check,
        )

        # Identify risk and opportunity factors
        risk_factors = self._identify_risk_factors(
            price_check,
            brand_check,
            keyword_check,
            triangulation_check,
            review_check,
            click_concentration_check,
        )

        opportunity_factors = self._identify_opportunities(
            price_check,
            brand_check,
            keyword_check,
            title_density_check,
        )

        # Generate recommendation
        recommendation = self._generate_recommendation(
            final_decision, overall_score, risk_factors, opportunity_factors
        )

        next_steps = self._generate_next_steps(final_decision, risk_factors)

        # Financial projections
        estimated_revenue = product.h10_monthly_revenue
        estimated_units = product.h10_monthly_sales
        estimated_margin = self._estimate_profit_margin(product)

        return ProductAnalysisResult(
            asin=product.asin,
            analyzed_at=datetime.now(),
            marketplace=product.marketplace,
            final_decision=final_decision,
            overall_score=overall_score,
            price_barrier_check=price_check,
            brand_dominance_check=brand_check,
            keyword_volume_check=keyword_check,
            review_velocity_check=review_check,
            title_density_check=title_density_check,
            click_concentration_check=click_concentration_check,
            triangulation_check=triangulation_check,
            risk_factors=risk_factors,
            opportunity_factors=opportunity_factors,
            estimated_monthly_revenue=estimated_revenue,
            estimated_monthly_units=estimated_units,
            estimated_profit_margin=estimated_margin,
            recommendation=recommendation,
            next_steps=next_steps,
        )

    def _calculate_weighted_score(
        self,
        price_check: AnalysisRule,
        brand_check: AnalysisRule,
        keyword_check: AnalysisRule,
        triangulation_check: AnalysisRule,
        review_check: Optional[AnalysisRule] = None,
        title_density_check: Optional[AnalysisRule] = None,
    ) -> float:
        """Calculate weighted overall score."""
        score = (
            price_check.score * settings.weight_price_barrier
            + brand_check.score * settings.weight_brand_dominance
            + keyword_check.score * settings.weight_keyword_volume
            + triangulation_check.score * settings.weight_triangulation
        )

        if review_check:
            score += review_check.score * settings.weight_review_velocity
        if title_density_check:
            score += title_density_check.score * settings.weight_title_density

        return min(100, max(0, score))

    def _determine_final_decision(
        self,
        overall_score: float,
        price_check: AnalysisRule,
        brand_check: AnalysisRule,
        keyword_check: AnalysisRule,
        triangulation_check: AnalysisRule,
    ) -> DecisionStatus:
        """
        Determine final decision with kill-switch logic.

        Any RED in critical checks = automatic RED decision.
        """
        # Kill switches (auto-reject)
        if price_check.status == DecisionStatus.RED:
            logger.warning("KILL SWITCH: Price barrier failed")
            return DecisionStatus.RED

        if brand_check.status == DecisionStatus.RED:
            logger.warning("KILL SWITCH: Brand dominance detected")
            return DecisionStatus.RED

        if keyword_check.status == DecisionStatus.RED:
            logger.warning("KILL SWITCH: Keyword volume insufficient")
            return DecisionStatus.RED

        # Score-based decision
        if overall_score >= settings.green_threshold:
            return DecisionStatus.GREEN
        elif overall_score >= settings.yellow_threshold:
            return DecisionStatus.YELLOW
        else:
            return DecisionStatus.RED

    def _identify_risk_factors(self, *checks) -> list[str]:
        """Extract risk factors from all checks."""
        risks = []
        for check in checks:
            if check and check.status in [DecisionStatus.RED, DecisionStatus.YELLOW]:
                risks.append(f"{check.rule_name}: {check.reason}")
        return risks

    def _identify_opportunities(self, *checks) -> list[str]:
        """Extract opportunity factors from checks."""
        opportunities = []
        for check in checks:
            if check and check.status == DecisionStatus.GREEN and check.score >= 80:
                opportunities.append(f"{check.rule_name}: {check.reason}")
        return opportunities

    def _generate_recommendation(
        self,
        decision: DecisionStatus,
        score: float,
        risks: list[str],
        opportunities: list[str],
    ) -> str:
        """Generate detailed recommendation text."""
        if decision == DecisionStatus.RED:
            return (
                f"❌ REJECT - Overall score: {score:.1f}/100. "
                f"This product fails critical criteria and should NOT be pursued. "
                f"Key issues: {len(risks)} risk factors identified. "
                f"Recommend searching for alternative products."
            )
        elif decision == DecisionStatus.YELLOW:
            return (
                f"⚠️ CAUTION - Overall score: {score:.1f}/100. "
                f"This product shows potential but has {len(risks)} concern(s). "
                f"Requires deeper manual analysis and validation. "
                f"Consider differentiation strategy before proceeding."
            )
        else:
            return (
                f"✅ APPROVE - Overall score: {score:.1f}/100. "
                f"This product meets all criteria and shows strong potential. "
                f"{len(opportunities)} positive factors identified. "
                f"Proceed with product development and supplier sourcing."
            )

    def _generate_next_steps(
        self, decision: DecisionStatus, risks: list[str]
    ) -> list[str]:
        """Generate actionable next steps."""
        if decision == DecisionStatus.RED:
            return [
                "Abandon this product opportunity",
                "Search for alternative products in the niche",
                "Review analysis criteria for learning",
            ]
        elif decision == DecisionStatus.YELLOW:
            steps = [
                "Conduct manual review of competitor listings",
                "Analyze negative reviews for differentiation opportunities",
                "Calculate detailed financial projections",
                "Develop unique value proposition",
            ]
            if any("monopoly" in r.lower() or "dominance" in r.lower() for r in risks):
                steps.append("Verify Amazon's private label presence manually")
            return steps
        else:
            return [
                "Source suppliers on Alibaba/1688",
                "Request product samples",
                "Calculate landed costs and margins",
                "Design packaging and branding",
                "Plan product launch strategy",
                "Prepare PPC campaign",
            ]

    def _fetch_keyword_data(self, keyword: str, marketplace: str) -> KeywordData:
        """Fetch keyword data from APIs."""
        volume = 0
        if self.h10_client:
            h10_data = self.h10_client.get_keyword_data(keyword, marketplace)
            volume = h10_data.get("search_volume", 0)

        if volume == 0 and self.ss_client:
            volume = self.ss_client.get_search_volume(keyword, marketplace) or 0

        return KeywordData(keyword=keyword, exact_search_volume=volume)

    def _analyze_review_velocity(
        self, product: ProductData, marketplace: str
    ) -> Optional[AnalysisRule]:
        """Analyze review velocity if data available."""
        # Implementation would use Helium 10's review velocity
        return None

    def _analyze_title_density(
        self, keyword: str, marketplace: str
    ) -> Optional[AnalysisRule]:
        """Analyze title density if data available."""
        if not self.h10_client:
            return None

        density = self.h10_client.get_title_density(keyword, marketplace)
        if density is None:
            return None

        # Title Density < 5 = ideal
        if density < 5:
            status = DecisionStatus.GREEN
            score = 100
            reason = f"Low title density ({density}). Great SEO opportunity."
        elif density < 7:
            status = DecisionStatus.YELLOW
            score = 60
            reason = f"Medium title density ({density}). Competitive but manageable."
        else:
            status = DecisionStatus.RED
            score = 20
            reason = f"High title density ({density}). Very competitive keyword."

        return AnalysisRule(
            rule_name="title_density",
            status=status,
            score=score,
            reason=reason,
            threshold_value=5.0,
            actual_value=density,
        )

    def _analyze_click_concentration(
        self, keyword: str, marketplace: str
    ) -> Optional[AnalysisRule]:
        """Analyze click concentration if data available."""
        if not self.ss_client:
            return None

        concentration = self.ss_client.get_click_concentration(keyword, marketplace)
        if concentration is None:
            return None

        # Already handled in brand_dominance, this is supplementary
        return None

    def _estimate_profit_margin(self, product: ProductData) -> Optional[float]:
        """Estimate profit margin based on price."""
        if not product.price:
            return None

        # Rule of Three: 1/3 COGS, 1/3 fees, 1/3 profit
        # Assume 15% referral + 20% FBA/PPC
        amazon_fees = product.price * 0.35
        estimated_cogs = product.price * 0.33
        estimated_profit = product.price - amazon_fees - estimated_cogs

        margin = (estimated_profit / product.price) * 100 if product.price > 0 else 0
        return max(0, min(100, margin))
