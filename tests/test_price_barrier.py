"""
Tests for Price Barrier Analyzer
"""

import pytest
from src.core.models import ProductData, Marketplace, DecisionStatus
from src.analyzers.price_barrier import PriceBarrierAnalyzer


class TestPriceBarrierAnalyzer:
    """Test suite for PriceBarrierAnalyzer."""

    def setup_method(self):
        """Setup test fixtures."""
        self.analyzer = PriceBarrierAnalyzer(min_price_usd=39.0)

    def test_price_below_threshold_red(self):
        """Test that prices well below threshold get RED status."""
        product = ProductData(
            asin="TEST001",
            title="Test Product",
            price=25.0,  # Below $39
            marketplace=Marketplace.US,
        )

        result = self.analyzer.analyze(product)

        assert result.status == DecisionStatus.RED
        assert result.score < 50
        assert result.threshold_value == 39.0
        assert result.actual_value == 25.0

    def test_price_at_threshold_yellow(self):
        """Test that prices near threshold get YELLOW status."""
        product = ProductData(
            asin="TEST002",
            title="Test Product",
            price=36.0,  # Close to $39
            marketplace=Marketplace.US,
        )

        result = self.analyzer.analyze(product)

        assert result.status == DecisionStatus.YELLOW
        assert 0 <= result.score < 50

    def test_price_above_threshold_green(self):
        """Test that prices above threshold get GREEN status."""
        product = ProductData(
            asin="TEST003",
            title="Test Product",
            price=49.0,  # Above $39
            marketplace=Marketplace.US,
        )

        result = self.analyzer.analyze(product)

        assert result.status == DecisionStatus.GREEN
        assert result.score >= 50

    def test_price_well_above_threshold_high_score(self):
        """Test that prices well above threshold get high scores."""
        product = ProductData(
            asin="TEST004",
            title="Test Product",
            price=79.0,  # Well above $39
            marketplace=Marketplace.US,
        )

        result = self.analyzer.analyze(product)

        assert result.status == DecisionStatus.GREEN
        assert result.score >= 80

    def test_eu_marketplace_uses_eur_threshold(self):
        """Test that EU marketplaces use EUR threshold."""
        analyzer = PriceBarrierAnalyzer(min_price_usd=39.0, min_price_eur=39.0)

        product_eu = ProductData(
            asin="TEST005",
            title="Test Product",
            price=45.0,
            marketplace=Marketplace.DE,
        )

        result = analyzer.analyze(product_eu)

        assert result.status == DecisionStatus.GREEN
        assert result.metadata["currency"] == "EUR"
