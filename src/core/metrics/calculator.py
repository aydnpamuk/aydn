"""
Amazon PPC Metrics Calculator

Calculates all core metrics: ACoS, TACOS, CTR, CVR, RPC, ROAS, CPC
Based on Amazon PPC & SEO Bible v3.0
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class MetricsResult:
    """Result of metrics calculation"""

    # Input data
    ad_spend: Decimal
    ad_sales: Decimal
    total_sales: Decimal
    impressions: Optional[int] = None
    clicks: Optional[int] = None
    orders: Optional[int] = None

    # Calculated metrics
    acos: Optional[Decimal] = None
    tacos: Optional[Decimal] = None
    roas: Optional[Decimal] = None
    ctr: Optional[Decimal] = None
    cvr: Optional[Decimal] = None
    rpc: Optional[Decimal] = None
    cpc: Optional[Decimal] = None

    def __post_init__(self):
        """Calculate all metrics after initialization"""
        self._calculate_all()

    def _calculate_all(self):
        """Calculate all available metrics"""
        # ACoS - Advertising Cost of Sale
        if self.ad_sales > 0:
            self.acos = (self.ad_spend / self.ad_sales) * 100

        # TACOS - Total Advertising Cost of Sale
        if self.total_sales > 0:
            self.tacos = (self.ad_spend / self.total_sales) * 100

        # ROAS - Return on Ad Spend
        if self.ad_spend > 0:
            self.roas = self.ad_sales / self.ad_spend

        # CTR - Click-Through Rate
        if self.impressions and self.impressions > 0 and self.clicks:
            self.ctr = (Decimal(self.clicks) / Decimal(self.impressions)) * 100

        # CVR - Conversion Rate
        if self.clicks and self.clicks > 0 and self.orders:
            self.cvr = (Decimal(self.orders) / Decimal(self.clicks)) * 100

        # RPC - Revenue Per Click
        if self.clicks and self.clicks > 0:
            self.rpc = self.ad_sales / Decimal(self.clicks)

        # CPC - Cost Per Click
        if self.clicks and self.clicks > 0:
            self.cpc = self.ad_spend / Decimal(self.clicks)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "ad_spend": float(self.ad_spend),
            "ad_sales": float(self.ad_sales),
            "total_sales": float(self.total_sales),
            "impressions": self.impressions,
            "clicks": self.clicks,
            "orders": self.orders,
            "acos": float(self.acos) if self.acos else None,
            "tacos": float(self.tacos) if self.tacos else None,
            "roas": float(self.roas) if self.roas else None,
            "ctr": float(self.ctr) if self.ctr else None,
            "cvr": float(self.cvr) if self.cvr else None,
            "rpc": float(self.rpc) if self.rpc else None,
            "cpc": float(self.cpc) if self.cpc else None,
        }


class MetricsCalculator:
    """Calculator for Amazon PPC metrics"""

    @staticmethod
    def calculate(
        ad_spend: float,
        ad_sales: float,
        total_sales: float,
        impressions: Optional[int] = None,
        clicks: Optional[int] = None,
        orders: Optional[int] = None,
    ) -> MetricsResult:
        """
        Calculate all PPC metrics

        Args:
            ad_spend: Total advertising spend
            ad_sales: Sales attributed to advertising
            total_sales: Total sales (organic + advertising)
            impressions: Number of ad impressions
            clicks: Number of ad clicks
            orders: Number of orders from ads

        Returns:
            MetricsResult with all calculated metrics

        Example:
            >>> calc = MetricsCalculator()
            >>> result = calc.calculate(
            ...     ad_spend=500,
            ...     ad_sales=2000,
            ...     total_sales=5000,
            ...     impressions=10000,
            ...     clicks=100,
            ...     orders=10
            ... )
            >>> print(f"ACoS: {result.acos}%")
            ACoS: 25.0%
        """
        return MetricsResult(
            ad_spend=Decimal(str(ad_spend)),
            ad_sales=Decimal(str(ad_sales)),
            total_sales=Decimal(str(total_sales)),
            impressions=impressions,
            clicks=clicks,
            orders=orders,
        )

    @staticmethod
    def calculate_acos(ad_spend: float, ad_sales: float) -> float:
        """
        Calculate ACoS (Advertising Cost of Sale)

        Formula: ACoS = (Ad Spend / Ad Sales) × 100

        Args:
            ad_spend: Total advertising spend
            ad_sales: Sales attributed to advertising

        Returns:
            ACoS as percentage

        Example:
            >>> MetricsCalculator.calculate_acos(500, 2000)
            25.0
        """
        if ad_sales == 0:
            return 0.0
        return (ad_spend / ad_sales) * 100

    @staticmethod
    def calculate_tacos(ad_spend: float, total_sales: float) -> float:
        """
        Calculate TACOS (Total Advertising Cost of Sale)

        Formula: TACOS = (Total Ad Spend / Total Sales) × 100

        Args:
            ad_spend: Total advertising spend
            total_sales: Total sales (organic + advertising)

        Returns:
            TACOS as percentage

        Example:
            >>> MetricsCalculator.calculate_tacos(500, 5000)
            10.0
        """
        if total_sales == 0:
            return 0.0
        return (ad_spend / total_sales) * 100

    @staticmethod
    def calculate_roas(ad_spend: float, ad_sales: float) -> float:
        """
        Calculate ROAS (Return on Ad Spend)

        Formula: ROAS = Ad Sales / Ad Spend

        Args:
            ad_spend: Total advertising spend
            ad_sales: Sales attributed to advertising

        Returns:
            ROAS as ratio

        Example:
            >>> MetricsCalculator.calculate_roas(500, 2000)
            4.0
        """
        if ad_spend == 0:
            return 0.0
        return ad_sales / ad_spend

    @staticmethod
    def calculate_ctr(impressions: int, clicks: int) -> float:
        """
        Calculate CTR (Click-Through Rate)

        Formula: CTR = (Clicks / Impressions) × 100

        Args:
            impressions: Number of ad impressions
            clicks: Number of ad clicks

        Returns:
            CTR as percentage

        Example:
            >>> MetricsCalculator.calculate_ctr(10000, 50)
            0.5
        """
        if impressions == 0:
            return 0.0
        return (clicks / impressions) * 100

    @staticmethod
    def calculate_cvr(clicks: int, orders: int) -> float:
        """
        Calculate CVR (Conversion Rate)

        Formula: CVR = (Orders / Clicks) × 100

        Args:
            clicks: Number of ad clicks
            orders: Number of orders from ads

        Returns:
            CVR as percentage

        Example:
            >>> MetricsCalculator.calculate_cvr(100, 10)
            10.0
        """
        if clicks == 0:
            return 0.0
        return (orders / clicks) * 100

    @staticmethod
    def calculate_rpc(total_sales: float, clicks: int) -> float:
        """
        Calculate RPC (Revenue Per Click)

        Formula: RPC = Total Sales / Total Clicks

        Args:
            total_sales: Total sales amount
            clicks: Total number of clicks

        Returns:
            RPC as currency amount

        Example:
            >>> MetricsCalculator.calculate_rpc(1000, 200)
            5.0
        """
        if clicks == 0:
            return 0.0
        return total_sales / clicks

    @staticmethod
    def calculate_cpc(ad_spend: float, clicks: int) -> float:
        """
        Calculate CPC (Cost Per Click)

        Formula: CPC = Total Spend / Total Clicks

        Args:
            ad_spend: Total advertising spend
            clicks: Total number of clicks

        Returns:
            CPC as currency amount

        Example:
            >>> MetricsCalculator.calculate_cpc(100, 50)
            2.0
        """
        if clicks == 0:
            return 0.0
        return ad_spend / clicks
