"""
Bid Optimization Formulas

RPC-based bid calculation and optimization strategies
Based on Amazon PPC & SEO Bible v3.0
"""

from dataclasses import dataclass
from typing import Optional
from decimal import Decimal


@dataclass
class BidRecommendation:
    """Bid optimization recommendation"""

    current_bid: Decimal
    recommended_bid: Decimal
    change_percentage: Decimal
    reason: str
    confidence: str  # high, medium, low

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "current_bid": float(self.current_bid),
            "recommended_bid": float(self.recommended_bid),
            "change_percentage": float(self.change_percentage),
            "reason": self.reason,
            "confidence": self.confidence,
        }


class RPCBidOptimizer:
    """
    RPC (Revenue Per Click) Based Bid Optimization

    Core Formula:
    Optimal Bid = RPC × Target ACoS

    Example:
        - RPC: $5 (Total Sales / Total Clicks)
        - Target ACoS: 25%
        - Optimal Bid: $5 × 0.25 = $1.25
    """

    @staticmethod
    def calculate_optimal_bid(
        total_sales: float, total_clicks: int, target_acos: float
    ) -> float:
        """
        Calculate optimal bid using RPC formula

        Args:
            total_sales: Total sales revenue
            total_clicks: Total number of clicks
            target_acos: Target ACoS as decimal (e.g., 0.25 for 25%)

        Returns:
            Optimal bid amount

        Raises:
            ValueError: If total_clicks is 0 or inputs are invalid

        Example:
            >>> RPCBidOptimizer.calculate_optimal_bid(1000, 200, 0.25)
            1.25
        """
        if total_clicks == 0:
            raise ValueError("Total clicks cannot be zero")

        if target_acos <= 0 or target_acos > 1:
            raise ValueError("Target ACoS must be between 0 and 1")

        rpc = total_sales / total_clicks
        optimal_bid = rpc * target_acos

        return round(optimal_bid, 2)

    @staticmethod
    def calculate_rpc(total_sales: float, total_clicks: int) -> float:
        """
        Calculate Revenue Per Click

        Args:
            total_sales: Total sales revenue
            total_clicks: Total number of clicks

        Returns:
            RPC value

        Example:
            >>> RPCBidOptimizer.calculate_rpc(1000, 200)
            5.0
        """
        if total_clicks == 0:
            return 0.0
        return total_sales / total_clicks

    @staticmethod
    def recommend_bid_adjustment(
        current_bid: float,
        total_sales: float,
        total_clicks: int,
        target_acos: float,
        current_acos: float,
        min_clicks_threshold: int = 20,
    ) -> BidRecommendation:
        """
        Recommend bid adjustment based on RPC and performance

        Args:
            current_bid: Current bid amount
            total_sales: Total sales revenue
            total_clicks: Total number of clicks
            target_acos: Target ACoS as decimal
            current_acos: Current ACoS as decimal
            min_clicks_threshold: Minimum clicks needed for reliable data

        Returns:
            BidRecommendation object

        Example:
            >>> rec = RPCBidOptimizer.recommend_bid_adjustment(
            ...     current_bid=2.0,
            ...     total_sales=1000,
            ...     total_clicks=200,
            ...     target_acos=0.25,
            ...     current_acos=0.40
            ... )
            >>> print(rec.recommended_bid)
            1.25
        """
        current_bid_decimal = Decimal(str(current_bid))

        # Check if we have enough data
        if total_clicks < min_clicks_threshold:
            return BidRecommendation(
                current_bid=current_bid_decimal,
                recommended_bid=current_bid_decimal,
                change_percentage=Decimal("0"),
                reason=f"Insufficient data ({total_clicks} clicks < {min_clicks_threshold} threshold)",
                confidence="low",
            )

        # Calculate optimal bid using RPC formula
        try:
            optimal_bid = RPCBidOptimizer.calculate_optimal_bid(
                total_sales, total_clicks, target_acos
            )
            optimal_bid_decimal = Decimal(str(optimal_bid))
        except ValueError as e:
            return BidRecommendation(
                current_bid=current_bid_decimal,
                recommended_bid=current_bid_decimal,
                change_percentage=Decimal("0"),
                reason=f"Calculation error: {str(e)}",
                confidence="low",
            )

        # Calculate change percentage
        if current_bid > 0:
            change_pct = ((optimal_bid - current_bid) / current_bid) * 100
        else:
            change_pct = 100.0

        change_pct_decimal = Decimal(str(round(change_pct, 2)))

        # Determine confidence based on data volume
        if total_clicks >= 100:
            confidence = "high"
        elif total_clicks >= 50:
            confidence = "medium"
        else:
            confidence = "low"

        # Generate reason
        if current_acos > target_acos:
            reason = f"ACoS ({current_acos:.1%}) above target ({target_acos:.1%}). Decrease bid to improve efficiency."
        elif current_acos < target_acos * 0.7:
            reason = f"ACoS ({current_acos:.1%}) well below target ({target_acos:.1%}). Increase bid to capture more volume."
        else:
            reason = f"ACoS ({current_acos:.1%}) near target ({target_acos:.1%}). Minor adjustment recommended."

        return BidRecommendation(
            current_bid=current_bid_decimal,
            recommended_bid=optimal_bid_decimal,
            change_percentage=change_pct_decimal,
            reason=reason,
            confidence=confidence,
        )


class PlacementModifierOptimizer:
    """
    Placement Modifier Optimization

    Based on Amazon PPC & SEO Bible v3.0:
    - Top of Search (TOS): Most visible, highest CPC
    - Rest of Search (ROS): Medium visibility, medium CPC
    - Product Pages (PP): Low visibility, lowest CPC, high intent
    """

    @staticmethod
    def recommend_tos_modifier(
        review_count: int,
        rating: float,
        price_competitive: bool,
        main_image_quality: str,  # excellent, good, average, poor
    ) -> int:
        """
        Recommend Top of Search placement modifier

        Args:
            review_count: Number of product reviews
            rating: Product rating (1-5)
            price_competitive: Whether price is competitive
            main_image_quality: Quality of main image

        Returns:
            Recommended modifier percentage (0, 50, 100, 200, 300)

        Example:
            >>> PlacementModifierOptimizer.recommend_tos_modifier(
            ...     review_count=250,
            ...     rating=4.6,
            ...     price_competitive=True,
            ...     main_image_quality="excellent"
            ... )
            100
        """
        # Poor listing - avoid TOS
        if review_count < 20 or rating < 4.0:
            return 0

        # Strong listing - aggressive TOS
        if (
            review_count >= 200
            and rating >= 4.5
            and price_competitive
            and main_image_quality in ["excellent", "good"]
        ):
            return 100

        # Branded keywords - very aggressive
        # (This would need keyword context, simplified here)
        if review_count >= 100 and rating >= 4.3:
            return 50

        # Default: neutral
        return 0

    @staticmethod
    def recommend_pp_modifier(
        campaign_type: str,  # competitor_conquest, complementary, category
        price_advantage: bool,
        competitor_rating_difference: float = 0,
    ) -> int:
        """
        Recommend Product Pages placement modifier

        Args:
            campaign_type: Type of product targeting campaign
            price_advantage: Whether you have price advantage
            competitor_rating_difference: Your rating - competitor rating

        Returns:
            Recommended modifier percentage

        Example:
            >>> PlacementModifierOptimizer.recommend_pp_modifier(
            ...     campaign_type="competitor_conquest",
            ...     price_advantage=True,
            ...     competitor_rating_difference=0.3
            ... )
            200
        """
        if campaign_type == "competitor_conquest":
            # Strong advantage - very aggressive
            if price_advantage and competitor_rating_difference >= 0.3:
                return 200
            # Some advantage - aggressive
            elif price_advantage or competitor_rating_difference >= 0.2:
                return 100
            # Neutral
            else:
                return 50

        elif campaign_type == "complementary":
            # Complementary products - moderate boost
            return 50

        else:  # category
            # Category targeting - conservative
            return 25


class BudgetPacingOptimizer:
    """
    Budget Pacing Optimization

    Ensures budget lasts throughout the day
    """

    @staticmethod
    def calculate_recommended_bid_adjustment(
        current_hour: int,
        budget_spent_percentage: float,
        target_end_percentage: float = 95,
    ) -> float:
        """
        Calculate bid adjustment to pace budget

        Args:
            current_hour: Current hour (0-23)
            budget_spent_percentage: Percentage of daily budget spent (0-100)
            target_end_percentage: Target budget utilization by end of day

        Returns:
            Recommended bid adjustment multiplier

        Example:
            >>> # At 10 AM, 50% budget spent (too fast)
            >>> BudgetPacingOptimizer.calculate_recommended_bid_adjustment(10, 50)
            0.85  # Decrease bids by 15%

            >>> # At 6 PM, 60% budget spent (good pace)
            >>> BudgetPacingOptimizer.calculate_recommended_bid_adjustment(18, 60)
            1.0  # No change
        """
        # Expected budget spent at this hour (linear pacing)
        expected_spent = (current_hour / 24) * target_end_percentage

        # If spending too fast, decrease bids
        if budget_spent_percentage > expected_spent * 1.2:
            return 0.80  # Decrease by 20%
        elif budget_spent_percentage > expected_spent * 1.1:
            return 0.85  # Decrease by 15%

        # If spending too slow, increase bids
        elif budget_spent_percentage < expected_spent * 0.7:
            return 1.20  # Increase by 20%
        elif budget_spent_percentage < expected_spent * 0.8:
            return 1.15  # Increase by 15%

        # On pace - no change
        return 1.0
