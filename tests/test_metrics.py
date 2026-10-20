# Method: pytest test functions with parametrize
# Objective: Check BR-03 (failure rate) and the risk classification against known values.

import pytest  # the testing library

from src.metrics import failure_rate_pct, risk_level  # the "calculator" we are testing


# One test function, run once per row below (one answer sheet, many rows)
@pytest.mark.parametrize(
    "failed, total, expected",
    [
        (162, 500, 32.4),   # real project numbers: overall failure rate
        (0, 10, 0.0),       # no failures at all
        (10, 10, 100.0),    # everything failed
    ],
)
def test_failure_rate_pct(failed, total, expected):
    # assert = "I claim this is true"; if it is false, pytest marks FAIL
    assert failure_rate_pct(failed, total) == expected


def test_failure_rate_pct_no_transactions_returns_none():
    # Zero transactions: there is no rate, so the rule returns None (not 0%)
    assert failure_rate_pct(0, 0) is None


@pytest.mark.parametrize(
    "rate, expected",
    [
        (41.03, "high"),
        (35, "high"),       # boundary: exactly 35 is already "high"
        (34.99, "medium"),  # just below the boundary
        (30, "medium"),     # boundary: exactly 30 is already "medium"
        (29.99, "low"),     # just below the boundary
        (0, "low"),
    ],
)
def test_risk_level(rate, expected):
    assert risk_level(rate) == expected