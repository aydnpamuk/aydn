"""
ACoS Management Decision Tree

Automated decision-making for ACoS optimization
Based on Amazon PPC & SEO Bible v3.0 - Chapter 12.1
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class DecisionAction(str, Enum):
    """Possible actions from decision tree"""

    WAIT = "wait"
    DECREASE_BID_20 = "decrease_bid_20"
    DECREASE_BID_40 = "decrease_bid_40"
    INCREASE_BID_15 = "increase_bid_15"
    INCREASE_BID_20 = "increase_bid_20"
    PAUSE_KEYWORD = "pause_keyword"
    NEGATIVE_KEYWORD = "negative_keyword"
    OPTIMIZE_LISTING = "optimize_listing"
    ADJUST_RPC = "adjust_rpc"
    SCALE_UP = "scale_up"
    NO_ACTION = "no_action"


class Confidence(str, Enum):
    """Confidence level in decision"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class ACoSDecision:
    """Decision result from ACoS analysis"""

    action: DecisionAction
    reason: str
    confidence: Confidence
    details: dict


class ACoSDecisionTree:
    """
    ACoS Management Decision Tree

    Flow based on Amazon PPC & SEO Bible v3.0:

    ACoS > 100% (Losing money per sale)
    ├── Clicks < 20 → WAIT (insufficient data)
    └── Clicks >= 20
        ├── CVR > 10% → Listing good, bid too high → DECREASE BID 40%
        └── CVR < 10% → Keyword-product mismatch → NEGATIVE

    ACoS 50-100% (High but has sales)
    ├── Clicks < 30 → WAIT (monitor trend)
    └── Clicks >= 30
        ├── CVR > Category avg → ADJUST with RPC formula
        └── CVR < Category avg → OPTIMIZE LISTING

    ACoS 30-50% (Above target)
    └── ADJUST with RPC formula

    ACoS 15-30% (Near target)
    └── MONITOR weekly, minor adjustments

    ACoS < 15% (Below target, very good)
    └── SCALE UP opportunity (increase bid, capture volume)
    """

    # Thresholds
    MIN_CLICKS_KEYWORD = 20
    MIN_CLICKS_RELIABLE = 30
    CATEGORY_AVG_CVR = 10.0  # 10% default category average
    EXCELLENT_ACOS = 15.0
    GOOD_ACOS = 30.0
    HIGH_ACOS = 50.0
    UNPROFITABLE_ACOS = 100.0

    @classmethod
    def evaluate(
        cls,
        acos: float,
        clicks: int,
        cvr: float,
        target_acos: Optional[float] = None,
        category_avg_cvr: Optional[float] = None,
    ) -> ACoSDecision:
        """
        Evaluate ACoS and return decision

        Args:
            acos: Current ACoS percentage (e.g., 67.0 for 67%)
            clicks: Number of clicks
            cvr: Conversion rate percentage (e.g., 8.0 for 8%)
            target_acos: Target ACoS percentage
            category_avg_cvr: Category average CVR percentage

        Returns:
            ACoSDecision with recommended action

        Example:
            >>> decision = ACoSDecisionTree.evaluate(
            ...     acos=67.0,
            ...     clicks=25,
            ...     cvr=8.0
            ... )
            >>> print(decision.action)
            DecisionAction.DECREASE_BID_40
        """
        if target_acos is None:
            target_acos = 25.0  # Default target

        if category_avg_cvr is None:
            category_avg_cvr = cls.CATEGORY_AVG_CVR

        # CRITICAL: ACoS > 100% (Losing money)
        if acos > cls.UNPROFITABLE_ACOS:
            return cls._handle_unprofitable(clicks, cvr)

        # HIGH: ACoS 50-100%
        elif acos >= cls.HIGH_ACOS:
            return cls._handle_high_acos(clicks, cvr, category_avg_cvr)

        # ABOVE TARGET: ACoS 30-50%
        elif acos >= cls.GOOD_ACOS:
            return cls._handle_above_target(clicks, target_acos, acos)

        # NEAR TARGET: ACoS 15-30%
        elif acos >= cls.EXCELLENT_ACOS:
            return cls._handle_near_target(acos, target_acos)

        # EXCELLENT: ACoS < 15%
        else:
            return cls._handle_excellent(acos, target_acos)

    @classmethod
    def _handle_unprofitable(cls, clicks: int, cvr: float) -> ACoSDecision:
        """Handle ACoS > 100% (unprofitable)"""
        if clicks < cls.MIN_CLICKS_KEYWORD:
            return ACoSDecision(
                action=DecisionAction.WAIT,
                reason=f"ACoS >100% but insufficient data ({clicks} clicks < {cls.MIN_CLICKS_KEYWORD} threshold). Wait for more data.",
                confidence=Confidence.LOW,
                details={
                    "clicks": clicks,
                    "threshold": cls.MIN_CLICKS_KEYWORD,
                    "cvr": cvr,
                },
            )

        # Enough data to decide
        if cvr > 10.0:
            # Good CVR means listing is working, bid is too high
            return ACoSDecision(
                action=DecisionAction.DECREASE_BID_40,
                reason=f"Losing money per sale (ACoS >100%) but CVR is good ({cvr:.1f}%). Listing converts well, bid is too high. Decrease bid by 40%.",
                confidence=Confidence.HIGH,
                details={
                    "clicks": clicks,
                    "cvr": cvr,
                    "bid_adjustment": -0.40,
                },
            )
        else:
            # Poor CVR means keyword-product mismatch
            return ACoSDecision(
                action=DecisionAction.NEGATIVE_KEYWORD,
                reason=f"Losing money per sale (ACoS >100%) and CVR is poor ({cvr:.1f}%). Keyword-product mismatch. Add to negative keywords.",
                confidence=Confidence.HIGH,
                details={
                    "clicks": clicks,
                    "cvr": cvr,
                    "threshold_cvr": 10.0,
                },
            )

    @classmethod
    def _handle_high_acos(
        cls, clicks: int, cvr: float, category_avg_cvr: float
    ) -> ACoSDecision:
        """Handle ACoS 50-100%"""
        if clicks < cls.MIN_CLICKS_RELIABLE:
            return ACoSDecision(
                action=DecisionAction.WAIT,
                reason=f"ACoS is high (50-100%) but data insufficient ({clicks} clicks). Monitor trend, wait for {cls.MIN_CLICKS_RELIABLE}+ clicks.",
                confidence=Confidence.LOW,
                details={
                    "clicks": clicks,
                    "threshold": cls.MIN_CLICKS_RELIABLE,
                    "cvr": cvr,
                },
            )

        # Enough data
        if cvr >= category_avg_cvr:
            # CVR is good, use RPC formula for bid adjustment
            return ACoSDecision(
                action=DecisionAction.ADJUST_RPC,
                reason=f"ACoS high but CVR good ({cvr:.1f}% vs {category_avg_cvr:.1f}% category avg). Use RPC formula for bid optimization.",
                confidence=Confidence.HIGH,
                details={
                    "clicks": clicks,
                    "cvr": cvr,
                    "category_avg_cvr": category_avg_cvr,
                },
            )
        else:
            # CVR below average, listing problem
            return ACoSDecision(
                action=DecisionAction.OPTIMIZE_LISTING,
                reason=f"ACoS high and CVR below category average ({cvr:.1f}% vs {category_avg_cvr:.1f}%). Listing optimization needed: CTR/CVR improvement.",
                confidence=Confidence.HIGH,
                details={
                    "clicks": clicks,
                    "cvr": cvr,
                    "category_avg_cvr": category_avg_cvr,
                },
            )

    @classmethod
    def _handle_above_target(cls, clicks: int, target_acos: float, acos: float) -> ACoSDecision:
        """Handle ACoS 30-50% (above target but not terrible)"""
        return ACoSDecision(
            action=DecisionAction.ADJUST_RPC,
            reason=f"ACoS ({acos:.1f}%) above target ({target_acos:.1f}%). Use RPC formula for precise bid adjustment.",
            confidence=Confidence.MEDIUM if clicks < 50 else Confidence.HIGH,
            details={
                "clicks": clicks,
                "current_acos": acos,
                "target_acos": target_acos,
            },
        )

    @classmethod
    def _handle_near_target(cls, acos: float, target_acos: float) -> ACoSDecision:
        """Handle ACoS 15-30% (near target, healthy range)"""
        if abs(acos - target_acos) <= 5:
            return ACoSDecision(
                action=DecisionAction.NO_ACTION,
                reason=f"ACoS ({acos:.1f}%) very close to target ({target_acos:.1f}%). Performance healthy, monitor weekly.",
                confidence=Confidence.HIGH,
                details={
                    "current_acos": acos,
                    "target_acos": target_acos,
                    "variance": abs(acos - target_acos),
                },
            )
        else:
            return ACoSDecision(
                action=DecisionAction.ADJUST_RPC,
                reason=f"ACoS ({acos:.1f}%) near target ({target_acos:.1f}%) but can be fine-tuned. Minor RPC-based adjustment.",
                confidence=Confidence.MEDIUM,
                details={
                    "current_acos": acos,
                    "target_acos": target_acos,
                },
            )

    @classmethod
    def _handle_excellent(cls, acos: float, target_acos: float) -> ACoSDecision:
        """Handle ACoS < 15% (excellent, opportunity to scale)"""
        efficiency_margin = target_acos - acos

        if efficiency_margin >= 10:
            # Very efficient, significant room to scale
            return ACoSDecision(
                action=DecisionAction.INCREASE_BID_20,
                reason=f"Excellent ACoS ({acos:.1f}%) well below target ({target_acos:.1f}%). Opportunity to scale up. Increase bid by 20% to capture more volume.",
                confidence=Confidence.HIGH,
                details={
                    "current_acos": acos,
                    "target_acos": target_acos,
                    "efficiency_margin": efficiency_margin,
                    "bid_adjustment": 0.20,
                },
            )
        else:
            # Efficient but closer to target
            return ACoSDecision(
                action=DecisionAction.INCREASE_BID_15,
                reason=f"Good ACoS ({acos:.1f}%) below target ({target_acos:.1f}%). Room to scale. Increase bid by 15% conservatively.",
                confidence=Confidence.MEDIUM,
                details={
                    "current_acos": acos,
                    "target_acos": target_acos,
                    "efficiency_margin": efficiency_margin,
                    "bid_adjustment": 0.15,
                },
            )
