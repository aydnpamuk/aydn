"""
Stockout Crisis Protocol

Emergency protocols for stock-out situations
Based on Amazon PPC & SEO Bible v3.0 - Chapter 13.1
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional


class StockLevel(str, Enum):
    """Stock level severity"""

    HEALTHY = "healthy"  # > 4 weeks
    WARNING = "warning"  # 2-4 weeks
    CRITICAL = "critical"  # 1-2 weeks
    EMERGENCY = "emergency"  # < 1 week
    OUT_OF_STOCK = "out_of_stock"  # 0 units


class ActionPriority(str, Enum):
    """Action priority levels"""

    IMMEDIATE = "immediate"  # Do now (0-24 hours)
    SHORT_TERM = "short_term"  # Do within 1-7 days
    MEDIUM_TERM = "medium_term"  # Do within 1-4 weeks


@dataclass
class StockAction:
    """Recommended action for stock crisis"""

    priority: ActionPriority
    action: str
    reason: str
    deadline: Optional[datetime] = None


@dataclass
class StockAnalysis:
    """Stock situation analysis"""

    current_stock: int
    daily_velocity: float
    days_remaining: float
    stock_level: StockLevel
    recommended_actions: List[StockAction]
    estimated_stockout_date: Optional[datetime] = None


class StockoutProtocol:
    """
    Stockout Crisis Management Protocol

    ⚠️ GOLDEN RULE #1: NEVER RUN OUT OF STOCK

    Running out of stock is the most costly mistake:
    - PPC campaigns reset
    - Organic ranking collapses
    - Recovery takes 2-4 weeks
    - Competitors fill the gap
    """

    # Thresholds
    HEALTHY_STOCK_WEEKS = 4
    WARNING_STOCK_WEEKS = 2
    CRITICAL_STOCK_WEEKS = 1

    @classmethod
    def analyze_stock_situation(
        cls,
        current_stock: int,
        daily_velocity: float,
        lead_time_days: int = 30,
    ) -> StockAnalysis:
        """
        Analyze current stock situation

        Args:
            current_stock: Current units in stock
            daily_velocity: Average daily sales
            lead_time_days: Reorder lead time in days

        Returns:
            StockAnalysis with recommendations

        Example:
            >>> analysis = StockoutProtocol.analyze_stock_situation(
            ...     current_stock=100,
            ...     daily_velocity=5.0,
            ...     lead_time_days=30
            ... )
            >>> print(analysis.stock_level)
            StockLevel.CRITICAL
        """
        if current_stock == 0:
            return cls._handle_out_of_stock()

        if daily_velocity == 0:
            # No sales, can't calculate
            return StockAnalysis(
                current_stock=current_stock,
                daily_velocity=0,
                days_remaining=float("inf"),
                stock_level=StockLevel.HEALTHY,
                recommended_actions=[],
            )

        days_remaining = current_stock / daily_velocity
        weeks_remaining = days_remaining / 7

        # Determine stock level
        if weeks_remaining < 1:
            stock_level = StockLevel.EMERGENCY
        elif weeks_remaining < 2:
            stock_level = StockLevel.CRITICAL
        elif weeks_remaining < 4:
            stock_level = StockLevel.WARNING
        else:
            stock_level = StockLevel.HEALTHY

        # Calculate estimated stockout date
        stockout_date = datetime.now() + timedelta(days=days_remaining)

        # Generate recommendations
        actions = cls._generate_actions(
            stock_level, days_remaining, lead_time_days, stockout_date
        )

        return StockAnalysis(
            current_stock=current_stock,
            daily_velocity=daily_velocity,
            days_remaining=days_remaining,
            stock_level=stock_level,
            recommended_actions=actions,
            estimated_stockout_date=stockout_date,
        )

    @classmethod
    def _handle_out_of_stock(cls) -> StockAnalysis:
        """Handle out of stock situation"""
        return StockAnalysis(
            current_stock=0,
            daily_velocity=0,
            days_remaining=0,
            stock_level=StockLevel.OUT_OF_STOCK,
            recommended_actions=[
                StockAction(
                    priority=ActionPriority.IMMEDIATE,
                    action="PAUSE ALL PPC CAMPAIGNS",
                    reason="No stock available. Prevent wasted ad spend.",
                    deadline=datetime.now(),
                ),
                StockAction(
                    priority=ActionPriority.IMMEDIATE,
                    action="Update listing with restock date",
                    reason="Manage customer expectations",
                    deadline=datetime.now(),
                ),
                StockAction(
                    priority=ActionPriority.IMMEDIATE,
                    action="Expedite emergency stock shipment",
                    reason="Minimize recovery time",
                    deadline=datetime.now() + timedelta(hours=24),
                ),
            ],
            estimated_stockout_date=datetime.now(),
        )

    @classmethod
    def _generate_actions(
        cls,
        stock_level: StockLevel,
        days_remaining: float,
        lead_time_days: int,
        stockout_date: datetime,
    ) -> List[StockAction]:
        """Generate recommended actions based on stock level"""
        actions = []

        if stock_level == StockLevel.EMERGENCY:
            # < 1 week of stock - IMMEDIATE ACTION
            actions.extend(
                [
                    StockAction(
                        priority=ActionPriority.IMMEDIATE,
                        action="PAUSE ALL PPC CAMPAIGNS",
                        reason=f"Stock critically low ({days_remaining:.1f} days). Preserve stock for organic sales.",
                        deadline=datetime.now(),
                    ),
                    StockAction(
                        priority=ActionPriority.IMMEDIATE,
                        action="Expedite air freight shipment",
                        reason="Standard lead time will cause stockout",
                        deadline=datetime.now() + timedelta(hours=24),
                    ),
                    StockAction(
                        priority=ActionPriority.IMMEDIATE,
                        action="Activate FBM backup plan",
                        reason="Bridge gap until FBA stock arrives",
                        deadline=datetime.now() + timedelta(hours=48),
                    ),
                    StockAction(
                        priority=ActionPriority.SHORT_TERM,
                        action="Reduce pricing or promotions",
                        reason="Slow down sales velocity to extend stock",
                        deadline=datetime.now() + timedelta(days=1),
                    ),
                ]
            )

        elif stock_level == StockLevel.CRITICAL:
            # 1-2 weeks of stock - URGENT
            actions.extend(
                [
                    StockAction(
                        priority=ActionPriority.IMMEDIATE,
                        action="Place emergency stock order",
                        reason=f"Stock will run out in {days_remaining:.1f} days. Lead time is {lead_time_days} days.",
                        deadline=datetime.now() + timedelta(hours=24),
                    ),
                    StockAction(
                        priority=ActionPriority.SHORT_TERM,
                        action="Reduce PPC budgets by 50%",
                        reason="Slow down sales velocity, extend stock",
                        deadline=datetime.now() + timedelta(days=1),
                    ),
                    StockAction(
                        priority=ActionPriority.SHORT_TERM,
                        action="Prepare FBM backup",
                        reason="Backup plan if FBA stockout occurs",
                        deadline=datetime.now() + timedelta(days=3),
                    ),
                    StockAction(
                        priority=ActionPriority.SHORT_TERM,
                        action="Contact supplier for expedited delivery",
                        reason="Standard lead time too long",
                        deadline=datetime.now() + timedelta(days=1),
                    ),
                ]
            )

        elif stock_level == StockLevel.WARNING:
            # 2-4 weeks of stock - WARNING
            actions.extend(
                [
                    StockAction(
                        priority=ActionPriority.SHORT_TERM,
                        action="Place regular stock reorder",
                        reason=f"Stock below {cls.HEALTHY_STOCK_WEEKS} week safety threshold",
                        deadline=datetime.now() + timedelta(days=3),
                    ),
                    StockAction(
                        priority=ActionPriority.SHORT_TERM,
                        action="Monitor daily sales velocity",
                        reason="Detect velocity changes early",
                        deadline=datetime.now() + timedelta(days=1),
                    ),
                    StockAction(
                        priority=ActionPriority.MEDIUM_TERM,
                        action="Review reorder point alerts",
                        reason="Prevent future close calls",
                        deadline=datetime.now() + timedelta(days=7),
                    ),
                ]
            )

        else:  # HEALTHY
            # > 4 weeks of stock - Maintain
            actions.extend(
                [
                    StockAction(
                        priority=ActionPriority.MEDIUM_TERM,
                        action="Continue normal operations",
                        reason="Stock levels healthy",
                        deadline=None,
                    ),
                    StockAction(
                        priority=ActionPriority.MEDIUM_TERM,
                        action="Weekly stock level monitoring",
                        reason="Maintain healthy stock buffer",
                        deadline=None,
                    ),
                ]
            )

        return actions

    @classmethod
    def calculate_reorder_point(
        cls,
        daily_velocity: float,
        lead_time_days: int,
        safety_stock_weeks: int = 2,
    ) -> int:
        """
        Calculate reorder point (when to place next order)

        Formula: Reorder Point = (Daily Velocity × Lead Time) + Safety Stock

        Args:
            daily_velocity: Average daily sales
            lead_time_days: Days to receive new stock
            safety_stock_weeks: Weeks of safety buffer

        Returns:
            Reorder point in units

        Example:
            >>> StockoutProtocol.calculate_reorder_point(
            ...     daily_velocity=5.0,
            ...     lead_time_days=30,
            ...     safety_stock_weeks=2
            ... )
            220  # (5 × 30) + (5 × 14)
        """
        lead_time_stock = daily_velocity * lead_time_days
        safety_stock = daily_velocity * (safety_stock_weeks * 7)
        reorder_point = lead_time_stock + safety_stock

        return int(reorder_point)

    @classmethod
    def should_pause_ppc(cls, days_remaining: float) -> bool:
        """
        Determine if PPC should be paused

        Args:
            days_remaining: Days of stock remaining

        Returns:
            True if PPC should be paused
        """
        return days_remaining < 7  # Less than 1 week

    @classmethod
    def calculate_budget_reduction(cls, days_remaining: float) -> float:
        """
        Calculate recommended PPC budget reduction

        Args:
            days_remaining: Days of stock remaining

        Returns:
            Reduction multiplier (0.0 = pause, 0.5 = 50% reduction, 1.0 = no change)
        """
        if days_remaining < 7:
            return 0.0  # Pause completely

        elif days_remaining < 14:
            return 0.5  # Reduce by 50%

        elif days_remaining < 28:
            return 0.75  # Reduce by 25%

        else:
            return 1.0  # No reduction
