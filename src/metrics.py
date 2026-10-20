# Method: Pure Python functions (no Spark, no database)
# Objective: Hold business rule BR-03 and the risk classification as testable code.

from typing import Optional  # lets us say a function may return a number OR None


def failure_rate_pct(failed: int, total: int) -> Optional[float]:
    """BR-03: failure rate = failed transactions / all transactions, in percent."""
    # With zero transactions there is no rate to calculate (and dividing by zero would crash)
    if total == 0:
        return None
    # Divide, convert to percent and round to 2 decimals (same as ROUND(..., 2) in SQL)
    return round(failed / total * 100, 2)


def risk_level(failure_rate: float) -> str:
    """Classify a category by failure rate: >= 35 high, >= 30 medium, else low."""
    # The first condition that is true wins, exactly like CASE WHEN in SQL
    if failure_rate >= 35:
        return "high"
    if failure_rate >= 30:
        return "medium"
    # Nothing above matched, so it is the ELSE case
    return "low"