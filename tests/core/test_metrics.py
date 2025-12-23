"""
Tests for Core Metrics Calculator
"""

import pytest
from decimal import Decimal
from src.core.metrics.calculator import MetricsCalculator, MetricsResult


class TestMetricsCalculator:
    """Test MetricsCalculator functionality"""

    def test_calculate_acos(self):
        """Test ACoS calculation"""
        acos = MetricsCalculator.calculate_acos(ad_spend=500, ad_sales=2000)
        assert acos == 25.0

    def test_calculate_acos_zero_sales(self):
        """Test ACoS with zero sales"""
        acos = MetricsCalculator.calculate_acos(ad_spend=500, ad_sales=0)
        assert acos == 0.0

    def test_calculate_tacos(self):
        """Test TACOS calculation"""
        tacos = MetricsCalculator.calculate_tacos(ad_spend=500, total_sales=5000)
        assert tacos == 10.0

    def test_calculate_roas(self):
        """Test ROAS calculation"""
        roas = MetricsCalculator.calculate_roas(ad_spend=500, ad_sales=2000)
        assert roas == 4.0

    def test_calculate_ctr(self):
        """Test CTR calculation"""
        ctr = MetricsCalculator.calculate_ctr(impressions=10000, clicks=50)
        assert ctr == 0.5

    def test_calculate_cvr(self):
        """Test CVR calculation"""
        cvr = MetricsCalculator.calculate_cvr(clicks=100, orders=10)
        assert cvr == 10.0

    def test_calculate_rpc(self):
        """Test RPC calculation"""
        rpc = MetricsCalculator.calculate_rpc(total_sales=1000, clicks=200)
        assert rpc == 5.0

    def test_calculate_cpc(self):
        """Test CPC calculation"""
        cpc = MetricsCalculator.calculate_cpc(ad_spend=100, clicks=50)
        assert cpc == 2.0

    def test_calculate_all_metrics(self):
        """Test calculating all metrics at once"""
        result = MetricsCalculator.calculate(
            ad_spend=500,
            ad_sales=2000,
            total_sales=5000,
            impressions=10000,
            clicks=100,
            orders=10,
        )

        assert isinstance(result, MetricsResult)
        assert float(result.acos) == 25.0
        assert float(result.tacos) == 10.0
        assert float(result.roas) == 4.0
        assert float(result.ctr) == 1.0
        assert float(result.cvr) == 10.0
        assert float(result.rpc) == 20.0
        assert float(result.cpc) == 5.0

    def test_metrics_result_to_dict(self):
        """Test MetricsResult to_dict conversion"""
        result = MetricsCalculator.calculate(
            ad_spend=500,
            ad_sales=2000,
            total_sales=5000,
        )

        data = result.to_dict()
        assert isinstance(data, dict)
        assert data["ad_spend"] == 500
        assert data["acos"] == 25.0
        assert data["tacos"] == 10.0
