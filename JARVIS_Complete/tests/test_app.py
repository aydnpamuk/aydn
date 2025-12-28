import pytest
from src.app import compute_roi


def test_compute_roi_positive() -> None:
    assert compute_roi(120, 100) == pytest.approx(0.2)


def test_compute_roi_zero_cost() -> None:
    assert compute_roi(100, 0) == 0.0
