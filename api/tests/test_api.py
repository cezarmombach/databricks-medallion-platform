# Method: pytest tests with FastAPI TestClient and a fake database function
# Objective: Check endpoints, filters, validation and error handling without touching Databricks.

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def fake_db(monkeypatch):
    """Replace run_query with a fake that records calls and returns canned rows."""

    class FakeDb:
        def __init__(self):
            self.rows = []      # what the fake "database" returns
            self.calls = []     # every (query, parameters) the API sent
            self.error = None   # set an exception here to simulate a failure

        def __call__(self, query, parameters=None):
            self.calls.append((query, parameters))
            if self.error:
                raise self.error
            return self.rows

    fake = FakeDb()
    monkeypatch.setattr("app.main.run_query", fake)
    return fake


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_failure_rate_returns_rows(client, fake_db):
    fake_db.rows = [{"category_name": "transport", "failure_rate_pct": 41.03}]
    response = client.get("/kpis/failure-rate")
    assert response.status_code == 200
    assert response.json() == fake_db.rows


def test_failure_rate_category_is_lowercased_and_parameterized(client, fake_db):
    fake_db.rows = [{"category_name": "transport"}]
    client.get("/kpis/failure-rate?category=TRANSPORT")
    query, parameters = fake_db.calls[0]
    assert parameters == {"category": "transport"}
    assert ":category" in query


def test_failure_rate_unknown_category_returns_404(client, fake_db):
    fake_db.rows = []
    response = client.get("/kpis/failure-rate?category=banana")
    assert response.status_code == 404
    assert response.json() == {"detail": "Category 'banana' not found"}


def test_sql_injection_attempt_stays_out_of_the_query_text(client, fake_db):
    fake_db.rows = []
    client.get("/kpis/failure-rate", params={"category": "x' OR 1=1 --"})
    query, parameters = fake_db.calls[0]
    assert "OR 1=1" not in query                       # never part of the SQL text
    assert parameters == {"category": "x' or 1=1 --"}  # only travels as a value


def test_monthly_category_filters_build_parameters(client, fake_db):
    client.get("/kpis/monthly-category?year=2026&month=9")
    query, parameters = fake_db.calls[0]
    assert "WHERE year = :year AND month = :month" in query
    assert parameters == {"year": 2026, "month": 9}


def test_monthly_category_without_filters_has_no_where(client, fake_db):
    client.get("/kpis/monthly-category")
    query, parameters = fake_db.calls[0]
    assert "WHERE" not in query
    assert parameters is None


def test_invalid_month_returns_422_and_never_queries(client, fake_db):
    response = client.get("/kpis/monthly-category?month=13")
    assert response.status_code == 422
    assert fake_db.calls == []


def test_database_failure_returns_503_without_leaking_details(client, fake_db):
    fake_db.error = RuntimeError("secret-token-123 failed")
    response = client.get("/kpis/monthly-balance")
    assert response.status_code == 503
    assert "secret-token-123" not in response.text