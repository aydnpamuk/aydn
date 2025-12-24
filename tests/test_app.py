"""Amazon PPC Vaka Avcısı - Testler."""

import pytest
from datetime import datetime

from ppc_agent.models import (
    CaseCandidate,
    Metrics,
    Platform,
    Market,
    Category,
    CaseType,
)
from ppc_agent.storage import CaseLibrary, get_current_week_id
from ppc_agent.scrapers import CaseAnalyzer


def test_metrics_count():
    """Test metric counting."""
    metrics = Metrics(acos=25.5, roas=3.5, cpc=0.85)
    assert metrics.count_available_metrics() == 3

    empty_metrics = Metrics()
    assert empty_metrics.count_available_metrics() == 0


def test_case_candidate_creation():
    """Test case candidate creation."""
    candidate = CaseCandidate(
        title="Test Case",
        url="https://example.com",
        date=datetime.now(),
        platform=Platform.REDDIT,
        market=Market.US,
        category=Category.OTHER,
        case_type=CaseType.LAUNCH,
        visible_metrics=["ACoS", "ROAS"],
        has_before_after=True,
        summary="Test summary",
        preliminary_confidence=75,
        confidence_reason="Good metrics and before/after data",
    )

    assert candidate.title == "Test Case"
    assert candidate.preliminary_confidence == 75
    assert len(candidate.visible_metrics) == 2


def test_get_current_week_id():
    """Test week ID generation."""
    week_id = get_current_week_id()
    assert week_id.startswith("2025-W") or week_id.startswith("2024-W")
    assert len(week_id) == 8


def test_preliminary_confidence_calculation():
    """Test preliminary confidence score calculation."""
    # High confidence: many metrics, before/after, high score
    score = CaseAnalyzer._calculate_preliminary_confidence(
        metrics=["ACoS", "ROAS", "CPC", "CTR"],
        has_before_after=True,
        score=50,
    )
    assert score >= 70

    # Low confidence: no metrics, no before/after
    score = CaseAnalyzer._calculate_preliminary_confidence(
        metrics=[],
        has_before_after=False,
        score=0,
    )
    assert score <= 40


def test_case_library_init(tmp_path):
    """Test case library initialization."""
    library = CaseLibrary(str(tmp_path / "test_library"))

    assert library.candidates_dir.exists()
    assert library.cases_dir.exists()
    assert library.reports_dir.exists()


def test_case_library_statistics(tmp_path):
    """Test library statistics."""
    library = CaseLibrary(str(tmp_path / "test_library"))
    stats = library.get_statistics()

    assert stats["total_candidates"] == 0
    assert stats["total_cases"] == 0
    assert stats["total_reports"] == 0
    assert stats["average_confidence_score"] == 0
