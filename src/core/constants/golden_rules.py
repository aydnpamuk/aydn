"""
Amazon PPC Golden Rules

The 5 unbreakable rules from Amazon PPC & SEO Bible v3.0
These are critical guidelines that must always be followed
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Optional


class RuleSeverity(str, Enum):
    """Severity level of rule violation"""

    CRITICAL = "critical"  # Business-threatening
    HIGH = "high"  # Significant impact
    MEDIUM = "medium"  # Moderate impact
    LOW = "low"  # Minor impact


@dataclass
class RuleViolation:
    """Represents a violation of a golden rule"""

    rule_number: int
    rule_name: str
    severity: RuleSeverity
    message: str
    recommended_action: str
    impact: str


class GoldenRules:
    """
    The 5 Golden Rules of Amazon PPC

    These rules are non-negotiable and form the foundation
    of any successful Amazon PPC strategy.
    """

    RULE_1_STOCK = """
    RULE #1: NEVER RUN OUT OF STOCK

    Running out of stock is the most costly and amateur mistake a seller can make.

    Why Critical:
    - PPC campaigns optimize based on historical order data
    - When stock runs out, all "velocity" metrics reset
    - Organic ranking collapses (Amazon sees product as "dead")
    - Recovery takes 2-4 weeks (honeymoon period lost)
    - Competitors fill the gap

    Prevention:
    - Maintain minimum 4-week stock buffer
    - Set reorder point alerts
    - Formula: Sales velocity × Lead time + Safety stock
    - Keep FBM backup plan ready
    """

    RULE_2_BUDGET = """
    RULE #2: NEVER EXHAUST BUDGET EARLY

    Daily budget running out early = Invisibility for rest of day

    Why Critical:
    - Budget exhausted at 10 AM = Zero visibility from 10 AM-midnight
    - Competitors dominate 60% of the day without competition
    - You lose market share silently

    Correct Approach:
    - Lower bids to stay visible throughout the day
    - More clicks = More data
    - Capture different time-of-day customer behaviors
    - Better dataset for optimization

    Practical Rule:
    - Daily budget should be max 70% spent by 6 PM
    - If budget hits 80%, decrease bids by 15-20%
    """

    RULE_3_ALWAYS_ADVERTISE = """
    RULE #3: ALWAYS RUN ADS (Never Pause Temporarily)

    Temporarily pausing ads directly kills sales velocity (momentum).

    Chain Reaction:
    1. Ads pause
    2. Sales slow down
    3. Amazon receives "product popularity declining" signal
    4. Organic ranking drops
    5. Organic sales also drop
    6. Even when ads resume, takes 2-4 weeks to recover

    Exceptions (ONLY these):
    - Stock critical (<1 week) → Pause ads, preserve stock
    - Listing suppressed → Fix listing first
    - Serious negative review crisis → Fix problem first
    """

    RULE_4_DATA_RESPECT = """
    RULE #4: RESPECT THE DATA

    Short-term data misleads.

    Data Reliability Timeline:
    - 3 days: Noise, unreliable
    - 7 days: Trend beginning, interpret carefully
    - 14 days: Reliable pattern
    - 30 days: Strategic decision foundation
    - 90 days: Seasonal and big picture

    Minimum Data Thresholds:
    - Keyword decision: 20+ clicks
    - Campaign decision: 100+ clicks
    - Product decision: 500+ clicks
    - A/B test: 1000+ impressions per variant
    """

    RULE_5_SEO_PPC_SYNERGY = """
    RULE #5: SEO AND PPC WORK TOGETHER

    They are not independent channels, they are an integrated system
    that feeds each other.

    PPC's Contribution to SEO:
    - Sales velocity increase → Organic rank rises
    - New keyword discovery → Added to SEO
    - CTR data → Listing optimization insights
    - Conversion data → Best performing messages

    SEO's Contribution to PPC:
    - Strong organic presence → Lower CPC (Amazon relevance reward)
    - Optimized listing → Higher CVR
    - Good reviews/rating → Higher CTR
    - Backend keywords → Wider PPC targeting

    Golden Ratio (Organic:PPC):
    - 3:1 or better → Healthy, sustainable
    - 2:1 → Normal growth
    - 1:1 → Aggressive growth or new product
    - 1:2 → Very aggressive, cash intensive
    - 10:1+ → PPC insufficient, missing opportunities
    """

    # Thresholds for rule violations
    MIN_STOCK_WEEKS = 4
    MAX_BUDGET_UTILIZATION_BY_HOUR = {
        12: 0.50,  # 50% by noon
        18: 0.70,  # 70% by 6 PM
        24: 0.95,  # 95% by end of day
    }
    MIN_CLICKS_KEYWORD = 20
    MIN_CLICKS_CAMPAIGN = 100
    MIN_CLICKS_PRODUCT = 500
    HEALTHY_ORGANIC_PPC_RATIO_MIN = 2.0  # 2:1 minimum


class GoldenRulesChecker:
    """Checker to validate compliance with golden rules"""

    @staticmethod
    def check_stock_level(
        current_stock: int, daily_sales_velocity: float, lead_time_days: int
    ) -> Optional[RuleViolation]:
        """
        Check Rule #1: Stock level

        Args:
            current_stock: Current stock units
            daily_sales_velocity: Average daily sales
            lead_time_days: Lead time to restock

        Returns:
            RuleViolation if violated, None if compliant
        """
        if daily_sales_velocity == 0:
            return None

        days_of_stock = current_stock / daily_sales_velocity
        required_stock_days = max(lead_time_days * 1.5, GoldenRules.MIN_STOCK_WEEKS * 7)

        if days_of_stock < 7:
            return RuleViolation(
                rule_number=1,
                rule_name="NEVER RUN OUT OF STOCK",
                severity=RuleSeverity.CRITICAL,
                message=f"Stock critically low: {days_of_stock:.1f} days remaining",
                recommended_action="IMMEDIATE: Pause PPC, expedite stock, activate FBM backup",
                impact="Campaign performance will reset if stock runs out. 2-4 week recovery period.",
            )
        elif days_of_stock < required_stock_days:
            return RuleViolation(
                rule_number=1,
                rule_name="NEVER RUN OUT OF STOCK",
                severity=RuleSeverity.HIGH,
                message=f"Stock below safety threshold: {days_of_stock:.1f} days (need {required_stock_days:.1f})",
                recommended_action="Place reorder immediately, monitor daily",
                impact="Risk of stockout which will destroy velocity and organic rank",
            )

        return None

    @staticmethod
    def check_budget_pacing(
        budget_spent_percentage: float, current_hour: int
    ) -> Optional[RuleViolation]:
        """
        Check Rule #2: Budget pacing

        Args:
            budget_spent_percentage: Percentage of daily budget spent (0-100)
            current_hour: Current hour (0-23)

        Returns:
            RuleViolation if violated, None if compliant
        """
        # Determine expected budget spent at this hour
        if current_hour >= 18:
            expected_max = GoldenRules.MAX_BUDGET_UTILIZATION_BY_HOUR[18] * 100
        elif current_hour >= 12:
            expected_max = GoldenRules.MAX_BUDGET_UTILIZATION_BY_HOUR[12] * 100
        else:
            return None  # Too early to judge

        if budget_spent_percentage > expected_max:
            return RuleViolation(
                rule_number=2,
                rule_name="NEVER EXHAUST BUDGET EARLY",
                severity=RuleSeverity.HIGH,
                message=f"Budget pacing too fast: {budget_spent_percentage:.1f}% spent at hour {current_hour}",
                recommended_action="Decrease bids by 15-20% to extend budget throughout day",
                impact="Competitors will dominate remaining hours with zero competition from you",
            )

        return None

    @staticmethod
    def check_campaign_active(campaigns_paused: int) -> Optional[RuleViolation]:
        """
        Check Rule #3: Always advertise

        Args:
            campaigns_paused: Number of campaigns currently paused

        Returns:
            RuleViolation if violated, None if compliant
        """
        if campaigns_paused > 0:
            return RuleViolation(
                rule_number=3,
                rule_name="ALWAYS RUN ADS",
                severity=RuleSeverity.HIGH,
                message=f"{campaigns_paused} campaign(s) currently paused",
                recommended_action="Resume campaigns unless stock critical, listing suppressed, or review crisis",
                impact="Sales velocity decreasing → Organic rank will drop → 2-4 week recovery",
            )

        return None

    @staticmethod
    def check_data_sufficiency(clicks: int, decision_type: str) -> Optional[RuleViolation]:
        """
        Check Rule #4: Data respect

        Args:
            clicks: Number of clicks
            decision_type: Type of decision (keyword, campaign, product)

        Returns:
            RuleViolation if making decision without enough data
        """
        thresholds = {
            "keyword": GoldenRules.MIN_CLICKS_KEYWORD,
            "campaign": GoldenRules.MIN_CLICKS_CAMPAIGN,
            "product": GoldenRules.MIN_CLICKS_PRODUCT,
        }

        required = thresholds.get(decision_type, 20)

        if clicks < required:
            return RuleViolation(
                rule_number=4,
                rule_name="RESPECT THE DATA",
                severity=RuleSeverity.MEDIUM,
                message=f"Insufficient data for {decision_type} decision: {clicks} clicks (need {required})",
                recommended_action="Wait for more data before making optimization decisions",
                impact="Decisions based on insufficient data lead to poor optimization",
            )

        return None

    @staticmethod
    def check_organic_ppc_balance(
        organic_sales: float, ppc_sales: float
    ) -> Optional[RuleViolation]:
        """
        Check Rule #5: SEO and PPC synergy

        Args:
            organic_sales: Organic sales amount
            ppc_sales: PPC sales amount

        Returns:
            RuleViolation if ratio is unhealthy
        """
        if ppc_sales == 0:
            return RuleViolation(
                rule_number=5,
                rule_name="SEO AND PPC WORK TOGETHER",
                severity=RuleSeverity.HIGH,
                message="No PPC sales - missing growth opportunities",
                recommended_action="Launch PPC campaigns to support organic growth",
                impact="Under-utilizing PPC means missing market share opportunities",
            )

        ratio = organic_sales / ppc_sales

        if ratio < 1:
            return RuleViolation(
                rule_number=5,
                rule_name="SEO AND PPC WORK TOGETHER",
                severity=RuleSeverity.MEDIUM,
                message=f"PPC-dependent: Organic:PPC ratio is {ratio:.1f}:1 (unhealthy)",
                recommended_action="Focus on SEO optimization to reduce PPC dependency",
                impact="Over-reliance on PPC is unsustainable and expensive long-term",
            )
        elif ratio > 10:
            return RuleViolation(
                rule_number=5,
                rule_name="SEO AND PPC WORK TOGETHER",
                severity=RuleSeverity.MEDIUM,
                message=f"Under-utilizing PPC: Organic:PPC ratio is {ratio:.1f}:1",
                recommended_action="Increase PPC investment to capture more market share",
                impact="Missing opportunities to accelerate growth and defend market position",
            )

        return None

    @staticmethod
    def check_all(
        current_stock: Optional[int] = None,
        daily_sales_velocity: Optional[float] = None,
        lead_time_days: Optional[int] = None,
        budget_spent_percentage: Optional[float] = None,
        current_hour: Optional[int] = None,
        campaigns_paused: Optional[int] = None,
        organic_sales: Optional[float] = None,
        ppc_sales: Optional[float] = None,
    ) -> List[RuleViolation]:
        """
        Check all golden rules

        Returns:
            List of violations found
        """
        violations = []

        # Rule 1: Stock
        if all(v is not None for v in [current_stock, daily_sales_velocity, lead_time_days]):
            violation = GoldenRulesChecker.check_stock_level(
                current_stock, daily_sales_velocity, lead_time_days
            )
            if violation:
                violations.append(violation)

        # Rule 2: Budget pacing
        if budget_spent_percentage is not None and current_hour is not None:
            violation = GoldenRulesChecker.check_budget_pacing(
                budget_spent_percentage, current_hour
            )
            if violation:
                violations.append(violation)

        # Rule 3: Always advertise
        if campaigns_paused is not None:
            violation = GoldenRulesChecker.check_campaign_active(campaigns_paused)
            if violation:
                violations.append(violation)

        # Rule 5: Organic/PPC balance
        if organic_sales is not None and ppc_sales is not None:
            violation = GoldenRulesChecker.check_organic_ppc_balance(
                organic_sales, ppc_sales
            )
            if violation:
                violations.append(violation)

        return violations
