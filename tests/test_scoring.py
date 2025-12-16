"""
Tests for Scoring Engine
"""

import pytest
from src.core.models import (
    ProductData,
    KeywordData,
    Marketplace,
    DecisionStatus,
)
from src.decision.scoring import ScoringEngine


class TestScoringEngine:
    """Test suite for ScoringEngine."""

    def setup_method(self):
        """Setup test fixtures."""
        self.engine = ScoringEngine(
            h10_client=None,  # Mock clients in real tests
            ss_client=None,
            keepa_client=None,
        )

    def test_kill_switch_low_price(self):
        """Test that low price triggers RED decision (kill switch)."""
        product = ProductData(
            asin="TEST001",
            title="Low Price Product",
            price=20.0,  # Below threshold
            marketplace=Marketplace.US,
        )

        keyword_data = KeywordData(keyword="test", exact_search_volume=5000)

        result = self.engine.analyze_product(product, "test", keyword_data)

        assert result.final_decision == DecisionStatus.RED
        assert "price" in str(result.recommendation).lower()

    def test_good_product_gets_green(self):
        """Test that product meeting all criteria gets GREEN."""
        product = ProductData(
            asin="TEST002",
            title="Good Product",
            price=49.0,  # Above threshold
            marketplace=Marketplace.US,
        )

        keyword_data = KeywordData(keyword="test", exact_search_volume=5000)

        result = self.engine.analyze_product(product, "test", keyword_data)

        # Should get GREEN or YELLOW (depending on other factors)
        assert result.final_decision in [DecisionStatus.GREEN, DecisionStatus.YELLOW]
        assert result.overall_score > 40

    def test_low_keyword_volume_triggers_red(self):
        """Test that low keyword volume triggers RED."""
        product = ProductData(
            asin="TEST003",
            title="Test Product",
            price=49.0,
            marketplace=Marketplace.US,
        )

        keyword_data = KeywordData(keyword="test", exact_search_volume=500)  # Too low

        result = self.engine.analyze_product(product, "test", keyword_data)

        assert result.final_decision == DecisionStatus.RED
        assert "keyword" in str(result.keyword_volume_check.reason).lower()

    def test_profit_margin_estimation(self):
        """Test profit margin estimation logic."""
        product = ProductData(
            asin="TEST004",
            title="Test Product",
            price=50.0,
            marketplace=Marketplace.US,
        )

        margin = self.engine._estimate_profit_margin(product)

        assert margin is not None
        assert 0 <= margin <= 100
        # For $50 product, expect roughly 30-35% margin
        assert 25 <= margin <= 40

    def test_scoring_weights_sum_to_one(self):
        """Test that scoring weights are properly balanced."""
        from src.core.config import settings

        total_weight = (
            settings.weight_price_barrier
            + settings.weight_brand_dominance
            + settings.weight_keyword_volume
            + settings.weight_review_velocity
            + settings.weight_title_density
            + settings.weight_triangulation
        )

        assert abs(total_weight - 1.0) < 0.01  # Allow small floating point error
