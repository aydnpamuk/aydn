"""
Amazon PPC Benchmark Standards

Industry benchmark values for CTR, CVR, ACoS, TACOS based on
Amazon PPC & SEO Bible v3.0
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class PerformanceLevel(str, Enum):
    """Performance level categories"""

    POOR = "poor"
    AVERAGE = "average"
    GOOD = "good"
    VERY_GOOD = "very_good"
    EXCELLENT = "excellent"


@dataclass
class BenchmarkRange:
    """Benchmark range with min/max values"""

    min_value: float
    max_value: Optional[float] = None
    level: PerformanceLevel = PerformanceLevel.AVERAGE

    def contains(self, value: float) -> bool:
        """Check if value falls within this range"""
        if self.max_value is None:
            return value >= self.min_value
        return self.min_value <= value < self.max_value


class CTRBenchmarks:
    """
    Click-Through Rate Benchmarks

    Based on Amazon PPC & SEO Bible v3.0:
    - Organic CTR: Higher due to trust signals
    - PPC CTR: Lower due to "ad blindness"
    """

    ORGANIC = {
        PerformanceLevel.POOR: BenchmarkRange(0, 1.5, PerformanceLevel.POOR),
        PerformanceLevel.AVERAGE: BenchmarkRange(1.5, 2.5, PerformanceLevel.AVERAGE),
        PerformanceLevel.GOOD: BenchmarkRange(2.5, 4.0, PerformanceLevel.GOOD),
        PerformanceLevel.VERY_GOOD: BenchmarkRange(
            4.0, 6.0, PerformanceLevel.VERY_GOOD
        ),
        PerformanceLevel.EXCELLENT: BenchmarkRange(6.0, None, PerformanceLevel.EXCELLENT),
    }

    PPC = {
        PerformanceLevel.POOR: BenchmarkRange(0, 0.3, PerformanceLevel.POOR),
        PerformanceLevel.AVERAGE: BenchmarkRange(0.3, 0.5, PerformanceLevel.AVERAGE),
        PerformanceLevel.GOOD: BenchmarkRange(0.5, 0.75, PerformanceLevel.GOOD),
        PerformanceLevel.VERY_GOOD: BenchmarkRange(
            0.75, 1.0, PerformanceLevel.VERY_GOOD
        ),
        PerformanceLevel.EXCELLENT: BenchmarkRange(1.0, None, PerformanceLevel.EXCELLENT),
    }

    @classmethod
    def evaluate_organic(cls, ctr: float) -> PerformanceLevel:
        """Evaluate organic CTR performance level"""
        for level, benchmark in cls.ORGANIC.items():
            if benchmark.contains(ctr):
                return level
        return PerformanceLevel.POOR

    @classmethod
    def evaluate_ppc(cls, ctr: float) -> PerformanceLevel:
        """Evaluate PPC CTR performance level"""
        for level, benchmark in cls.PPC.items():
            if benchmark.contains(ctr):
                return level
        return PerformanceLevel.POOR


class CVRBenchmarks:
    """
    Conversion Rate Benchmarks

    Category-dependent, these are general guidelines
    """

    GENERAL = {
        PerformanceLevel.POOR: BenchmarkRange(0, 5, PerformanceLevel.POOR),
        PerformanceLevel.AVERAGE: BenchmarkRange(5, 10, PerformanceLevel.AVERAGE),
        PerformanceLevel.GOOD: BenchmarkRange(10, 15, PerformanceLevel.GOOD),
        PerformanceLevel.VERY_GOOD: BenchmarkRange(
            15, 20, PerformanceLevel.VERY_GOOD
        ),
        PerformanceLevel.EXCELLENT: BenchmarkRange(20, None, PerformanceLevel.EXCELLENT),
    }

    @classmethod
    def evaluate(cls, cvr: float) -> PerformanceLevel:
        """Evaluate CVR performance level"""
        for level, benchmark in cls.GENERAL.items():
            if benchmark.contains(cvr):
                return level
        return PerformanceLevel.POOR


class ACoSBenchmarks:
    """
    ACoS (Advertising Cost of Sale) Benchmarks

    Lower is better, but context matters:
    - New products: Higher ACoS acceptable
    - Mature products: Lower ACoS expected
    """

    GENERAL = {
        PerformanceLevel.EXCELLENT: BenchmarkRange(0, 15, PerformanceLevel.EXCELLENT),
        PerformanceLevel.GOOD: BenchmarkRange(15, 20, PerformanceLevel.GOOD),
        PerformanceLevel.AVERAGE: BenchmarkRange(20, 35, PerformanceLevel.AVERAGE),
        PerformanceLevel.POOR: BenchmarkRange(35, 50, PerformanceLevel.POOR),
        # > 50% is typically unprofitable
    }

    @classmethod
    def evaluate(cls, acos: float) -> PerformanceLevel:
        """Evaluate ACoS performance level"""
        if acos > 50:
            return PerformanceLevel.POOR

        for level, benchmark in cls.GENERAL.items():
            if benchmark.contains(acos):
                return level
        return PerformanceLevel.POOR


class TACoSBenchmarks:
    """
    TACOS (Total Advertising Cost of Sale) Benchmarks

    Indicates advertising dependency:
    - < 5%: Under-investing (may miss opportunities)
    - 8-12%: Healthy balance
    - > 20%: Over-reliance on ads
    """

    STRATEGY_MAP = {
        "insufficient": BenchmarkRange(0, 5),
        "conservative": BenchmarkRange(5, 8),
        "standard": BenchmarkRange(8, 12),
        "aggressive": BenchmarkRange(12, 20),
        "ultra_aggressive": BenchmarkRange(20, None),
    }

    @classmethod
    def evaluate_strategy(cls, tacos: float) -> str:
        """
        Evaluate TACOS strategy level

        Returns:
            Strategy name: insufficient, conservative, standard, aggressive, ultra_aggressive
        """
        for strategy, benchmark in cls.STRATEGY_MAP.items():
            if benchmark.contains(tacos):
                return strategy
        return "insufficient"

    @classmethod
    def is_healthy(cls, tacos: float) -> bool:
        """Check if TACOS is in healthy range (8-12%)"""
        return 8 <= tacos <= 12


class OrganicPPCRatioBenchmarks:
    """
    Organic to PPC Sales Ratio Benchmarks

    Healthy: 3:1 or better (75% organic, 25% PPC)
    """

    @staticmethod
    def calculate_ratio(organic_sales: float, ppc_sales: float) -> float:
        """
        Calculate organic to PPC ratio

        Args:
            organic_sales: Organic sales amount
            ppc_sales: PPC sales amount

        Returns:
            Ratio as float (e.g., 3.0 means 3:1)
        """
        if ppc_sales == 0:
            return float("inf")  # All organic
        return organic_sales / ppc_sales

    @staticmethod
    def evaluate(ratio: float) -> str:
        """
        Evaluate organic:PPC ratio health

        Returns:
            Health status: excellent, healthy, normal, aggressive, very_aggressive, insufficient
        """
        if ratio >= 10:
            return "insufficient_ppc"  # Under-utilizing PPC
        elif ratio >= 3:
            return "excellent"  # 3:1 or better
        elif ratio >= 2:
            return "healthy"  # 2:1
        elif ratio >= 1:
            return "normal"  # 1:1 balanced growth
        elif ratio >= 0.5:
            return "aggressive"  # 1:2 very aggressive
        else:
            return "very_aggressive"  # High PPC dependency


class BenchmarkEvaluator:
    """Unified benchmark evaluator"""

    @staticmethod
    def evaluate_all(
        ctr_ppc: Optional[float] = None,
        ctr_organic: Optional[float] = None,
        cvr: Optional[float] = None,
        acos: Optional[float] = None,
        tacos: Optional[float] = None,
        organic_sales: Optional[float] = None,
        ppc_sales: Optional[float] = None,
    ) -> dict:
        """
        Evaluate all metrics against benchmarks

        Returns:
            Dictionary with evaluation results
        """
        results = {}

        if ctr_ppc is not None:
            results["ctr_ppc"] = {
                "value": ctr_ppc,
                "level": CTRBenchmarks.evaluate_ppc(ctr_ppc),
            }

        if ctr_organic is not None:
            results["ctr_organic"] = {
                "value": ctr_organic,
                "level": CTRBenchmarks.evaluate_organic(ctr_organic),
            }

        if cvr is not None:
            results["cvr"] = {
                "value": cvr,
                "level": CVRBenchmarks.evaluate(cvr),
            }

        if acos is not None:
            results["acos"] = {
                "value": acos,
                "level": ACoSBenchmarks.evaluate(acos),
            }

        if tacos is not None:
            results["tacos"] = {
                "value": tacos,
                "strategy": TACoSBenchmarks.evaluate_strategy(tacos),
                "is_healthy": TACoSBenchmarks.is_healthy(tacos),
            }

        if organic_sales is not None and ppc_sales is not None:
            ratio = OrganicPPCRatioBenchmarks.calculate_ratio(organic_sales, ppc_sales)
            results["organic_ppc_ratio"] = {
                "ratio": ratio,
                "health": OrganicPPCRatioBenchmarks.evaluate(ratio),
            }

        return results
