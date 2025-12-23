"""
Tests for ACoS Decision Tree
"""

import pytest
from src.decision.acos.manager import ACoSDecisionTree, DecisionAction, Confidence


class TestACoSDecisionTree:
    """Test ACoS Decision Tree logic"""

    def test_unprofitable_insufficient_data(self):
        """Test ACoS >100% with insufficient data"""
        decision = ACoSDecisionTree.evaluate(
            acos=120.0,
            clicks=15,  # < 20 threshold
            cvr=8.0,
        )

        assert decision.action == DecisionAction.WAIT
        assert decision.confidence == Confidence.LOW
        assert "insufficient data" in decision.reason.lower()

    def test_unprofitable_good_cvr(self):
        """Test ACoS >100% with good CVR (bid too high)"""
        decision = ACoSDecisionTree.evaluate(
            acos=120.0,
            clicks=25,
            cvr=12.0,  # > 10%
        )

        assert decision.action == DecisionAction.DECREASE_BID_40
        assert decision.confidence == Confidence.HIGH
        assert "decrease bid by 40%" in decision.reason.lower()

    def test_unprofitable_poor_cvr(self):
        """Test ACoS >100% with poor CVR (keyword mismatch)"""
        decision = ACoSDecisionTree.evaluate(
            acos=120.0,
            clicks=25,
            cvr=5.0,  # < 10%
        )

        assert decision.action == DecisionAction.NEGATIVE_KEYWORD
        assert decision.confidence == Confidence.HIGH
        assert "mismatch" in decision.reason.lower()

    def test_high_acos_insufficient_data(self):
        """Test ACoS 50-100% with insufficient data"""
        decision = ACoSDecisionTree.evaluate(
            acos=60.0,
            clicks=25,  # < 30 threshold
            cvr=8.0,
        )

        assert decision.action == DecisionAction.WAIT
        assert decision.confidence == Confidence.LOW

    def test_high_acos_good_cvr(self):
        """Test ACoS 50-100% with good CVR"""
        decision = ACoSDecisionTree.evaluate(
            acos=60.0,
            clicks=50,
            cvr=12.0,  # > 10% category avg
        )

        assert decision.action == DecisionAction.ADJUST_RPC
        assert decision.confidence == Confidence.HIGH

    def test_high_acos_poor_cvr(self):
        """Test ACoS 50-100% with poor CVR"""
        decision = ACoSDecisionTree.evaluate(
            acos=60.0,
            clicks=50,
            cvr=6.0,  # < 10% category avg
        )

        assert decision.action == DecisionAction.OPTIMIZE_LISTING
        assert decision.confidence == Confidence.HIGH

    def test_above_target_acos(self):
        """Test ACoS 30-50%"""
        decision = ACoSDecisionTree.evaluate(
            acos=40.0,
            clicks=50,
            cvr=10.0,
            target_acos=25.0,
        )

        assert decision.action == DecisionAction.ADJUST_RPC
        assert decision.confidence == Confidence.HIGH

    def test_near_target_acos_close(self):
        """Test ACoS very close to target"""
        decision = ACoSDecisionTree.evaluate(
            acos=23.0,
            clicks=50,
            cvr=10.0,
            target_acos=25.0,
        )

        assert decision.action == DecisionAction.NO_ACTION
        assert decision.confidence == Confidence.HIGH

    def test_excellent_acos_significant_margin(self):
        """Test ACoS <15% with significant efficiency margin"""
        decision = ACoSDecisionTree.evaluate(
            acos=10.0,
            clicks=50,
            cvr=12.0,
            target_acos=25.0,
        )

        assert decision.action == DecisionAction.INCREASE_BID_20
        assert decision.confidence == Confidence.HIGH
        assert decision.details["bid_adjustment"] == 0.20

    def test_excellent_acos_moderate_margin(self):
        """Test ACoS <15% with moderate efficiency margin"""
        decision = ACoSDecisionTree.evaluate(
            acos=12.0,
            clicks=50,
            cvr=12.0,
            target_acos=20.0,
        )

        assert decision.action == DecisionAction.INCREASE_BID_15
        assert decision.confidence == Confidence.MEDIUM
        assert decision.details["bid_adjustment"] == 0.15
