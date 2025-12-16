"""
Price Barrier Analyzer

Implements the $39/€39 rule from the research report.
Products below this threshold are typically rejected due to:
- Amazon fee structure eating into margins
- Difficulty achieving 20-30% profit margin
- Fixed costs eroding profits on low-priced items
"""

import logging
from typing import Optional
from ..core.models import AnalysisRule, DecisionStatus, ProductData, Marketplace
from ..core.config import settings

logger = logging.getLogger(__name__)


class PriceBarrierAnalyzer:
    """
    Analyzes products against the price barrier rule.

    Research basis:
    - Rule of Three: 1/3 COGS, 1/3 Amazon fees, 1/3 profit
    - Amazon fees: 8-15% referral + FBA fulfillment + storage + PPC (15-25% TACoS)
    - $30 product ≈ $10 net profit (too low for sustainability)
    """

    def __init__(
        self,
        min_price_usd: Optional[float] = None,
        min_price_eur: Optional[float] = None,
    ):
        """
        Initialize price barrier analyzer.

        Args:
            min_price_usd: Minimum price for US market (default from config)
            min_price_eur: Minimum price for EU markets (default from config)
        """
        self.min_price_usd = min_price_usd or settings.price_barrier_usd
        self.min_price_eur = min_price_eur or settings.price_barrier_eur

    def analyze(self, product: ProductData) -> AnalysisRule:
        """
        Analyze product price against barrier threshold.

        Args:
            product: Product data to analyze

        Returns:
            AnalysisRule: Analysis result with status and reasoning
        """
        price = product.price
        marketplace = product.marketplace

        # Determine threshold based on marketplace
        if marketplace in [
            Marketplace.US,
            Marketplace.CA,
        ]:
            threshold = self.min_price_usd
            currency = "USD"
        else:
            threshold = self.min_price_eur
            currency = "EUR"

        logger.info(
            f"Analyzing price barrier for {product.asin}: "
            f"${price} vs ${threshold} threshold"
        )

        # Calculate score (0-100)
        if price < threshold * 0.7:
            # Severely under threshold
            score = 0.0
            status = DecisionStatus.RED
            reason = (
                f"Price ${price:.2f} is severely below the ${threshold} barrier. "
                f"Profit margins will be unsustainable due to Amazon fees "
                f"(referral + FBA + storage + PPC). Expected margin erosion."
            )

        elif price < threshold:
            # Under threshold but close
            score = (price / threshold) * 50  # 0-50 range
            status = DecisionStatus.YELLOW
            reason = (
                f"Price ${price:.2f} is below the recommended ${threshold} threshold. "
                f"Tight margins expected. Consider only if lightweight product "
                f"with low FBA fees."
            )

        elif price < threshold * 1.5:
            # Above threshold - good range
            score = 50 + ((price - threshold) / (threshold * 0.5)) * 30  # 50-80 range
            status = DecisionStatus.GREEN
            reason = (
                f"Price ${price:.2f} meets the barrier requirement. "
                f"Adequate margin potential for 20-30% profit after fees."
            )

        else:
            # Well above threshold - excellent
            score = min(100, 80 + ((price - threshold * 1.5) / threshold) * 20)
            status = DecisionStatus.GREEN
            reason = (
                f"Price ${price:.2f} is well above threshold. "
                f"Strong profit margin potential (30%+). Excellent price point."
            )

        return AnalysisRule(
            rule_name="price_barrier",
            status=status,
            score=score,
            reason=reason,
            threshold_value=threshold,
            actual_value=price,
            metadata={
                "currency": currency,
                "marketplace": marketplace.value,
                "price_to_threshold_ratio": price / threshold if threshold > 0 else 0,
            },
        )

    def get_recommended_price_range(
        self, marketplace: Marketplace
    ) -> tuple[float, float]:
        """
        Get recommended price range for a marketplace.

        Args:
            marketplace: Target marketplace

        Returns:
            tuple: (min_price, optimal_price)
        """
        if marketplace in [Marketplace.US, Marketplace.CA]:
            return (self.min_price_usd, self.min_price_usd * 1.5)
        else:
            return (self.min_price_eur, self.min_price_eur * 1.5)
