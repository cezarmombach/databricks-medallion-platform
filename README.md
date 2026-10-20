# Databricks Medallion Platform

A financial transactions data platform built on **Databricks Free Edition** following the **medallion architecture** (bronze, silver, gold), using PySpark and SQL on Delta Lake with Unity Catalog.

> Learning project. All data is synthetic. No real financial data is used.

## What it does

Raw transactions flow through three layers, each one cleaner and closer to the business:

| Layer | Schema | Purpose |
|-------|--------|---------|
| Bronze | `workspace.bronze` | Raw data, kept as received |
| Silver | `workspace.silver` | Typed, cleaned and deduplicated data |
| Gold | `workspace.gold` | Star schema and business marts, ready for analytics |

## Gold layer

**Star schema** (grain: one row per transaction):
- `fact_transactions` (500 transactions)
- `dim_date`, `dim_category`, `dim_account`
- Surrogate keys generated with `xxhash64`

**Marts** (official KPIs):
- `mart_monthly_category`: total per month and category (BR-01: only `completed` transactions)
- `mart_monthly_balance`: net balance per month (BR-02: net = inflow - outflow, `unknown` excluded)
- `mart_failure_rate_category`: failure rate per category (BR-03: failed / all transactions)

## Other topics covered

- **Window functions:** `LAG`, running total, `RANK` / `DENSE_RANK`
- **Advanced SQL:** CTEs, Top-N, subqueries, `CASE WHEN`, `HAVING`
- **SCD Type 2:** `dim_account_scd2` with `valid_from`, `valid_to`, `is_current` and a point-in-time join
- **Materialized view:** `mv_failure_rate_category` (see `sql/`)
- **Data quality:** 13 automated checks (uniqueness, nulls, orphan keys, accepted values, ranges, reconciliation) with a fail-fast gate

## Repository structure

```text
notebooks/   Databricks notebooks, numbered in execution order (01 to 11)
sql/         SQL files for objects created outside notebooks
```

## How to run

1. Create a free [Databricks Free Edition](https://www.databricks.com/learn/free-edition) workspace.
2. Clone this repository as a Git folder.
3. Run the notebooks in numeric order.
4. Create the materialized view from `sql/` using the SQL Editor (it needs a SQL warehouse).

## Roadmap

- [ ] pytest and CI with GitHub Actions
- [ ] Orchestration with Databricks Workflows and Airflow
- [ ] Power BI dashboard
- [ ] GCP version (BigQuery, Pub/Sub)
- [ ] Docker and FastAPI