# Method: FastAPI application with KPI endpoints, validated filters and safe errors
# Objective: Serve the gold-layer marts as JSON without leaking internal details.

import logging

from fastapi import FastAPI, HTTPException, Query

from app.db import run_query

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Medallion KPI API",
    description="Serves gold-layer KPIs from the Databricks medallion platform.",
    version="0.2.0",
)


def fetch(query: str, parameters: dict | None = None) -> list[dict]:
    """Run a query; on any failure, log the real error and return a generic 503."""
    try:
        return run_query(query, parameters)
    except Exception:
        # The full error goes to the server log, never to the client
        logger.exception("Query failed")
        raise HTTPException(status_code=503, detail="Data source unavailable, try again later")


@app.get("/health")
def health():
    # Used by people, Docker and monitoring tools to check that the API is up
    return {"status": "ok"}


@app.get("/kpis/monthly-balance")
def monthly_balance():
    # Official net balance per month (BR-02), precomputed in the gold layer
    return fetch("SELECT * FROM workspace.gold.mart_monthly_balance ORDER BY year, month")


@app.get("/kpis/failure-rate")
def failure_rate(category: str | None = None):
    # Failure rate per category (BR-03), optionally for one category
    if category is None:
        return fetch(
            "SELECT * FROM workspace.gold.mart_failure_rate_category "
            "ORDER BY failure_rate_pct DESC"
        )

    rows = fetch(
        "SELECT * FROM workspace.gold.mart_failure_rate_category "
        "WHERE category_name = :category",
        {"category": category.lower()},  # category names are stored in lowercase
    )
    if not rows:
        raise HTTPException(status_code=404, detail=f"Category '{category}' not found")
    return rows


@app.get("/kpis/monthly-category")
def monthly_category(
    year: int | None = None,
    month: int | None = Query(default=None, ge=1, le=12),  # reject months outside 1..12
):
    # Completed amount per month and category (BR-01), with optional filters
    conditions = []
    parameters = {}
    if year is not None:
        conditions.append("year = :year")
        parameters["year"] = year
    if month is not None:
        conditions.append("month = :month")
        parameters["month"] = month

    where = f"WHERE {' AND '.join(conditions)} " if conditions else ""
    return fetch(
        "SELECT * FROM workspace.gold.mart_monthly_category "
        + where
        + "ORDER BY year, month, category_name",
        parameters or None,
    )