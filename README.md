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

The source data is generated with a fixed random seed (reproducible) and contains intentional dirty data (missing categories, inconsistent casing, comma decimal separators and duplicated rows), which is cleaned in the silver layer.

## Dashboard

A Power BI report (Import mode) built on the gold layer. Its measures match the marts built in Databricks. See [`powerbi/`](powerbi/) for the data model and the DAX measures.

![Dashboard overview](powerbi/dashboard_overview.png)

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

## Quality and testing

There are two kinds of tests, and each one catches errors the other cannot:

| | What it checks | Where it runs |
|---|---|---|
| **Data quality** (`11_data_quality`) | The **real data**: uniqueness, nulls, orphan keys, accepted values, ranges and reconciliation between layers (13 checks) | In Databricks, as the last task of the pipeline |
| **Unit tests** (`tests/`) | The **code**: business rules in `src/metrics.py`, with known inputs and expected outputs (pytest) | Locally, in a notebook and in GitHub Actions |

The data quality notebook ends with a fail-fast `assert`: if any check fails, the job stops and sends an alert.

**Continuous integration:** a GitHub Actions workflow runs two jobs on every push to `main` and on pull requests: the pytest suite for `src/` and the API tests in `api/`.

## Orchestration

The pipeline runs as a **Databricks job** (`medallion_pipeline`), one task per notebook, in this order:

```text
setup -> bronze_ingestion -> silver_transformation -> gold_modeling_1 -> gold_modeling_2 -> gold_modeling_3 -> gold_marts -> data_quality_gate
```

- Every write uses `overwrite` (or `CREATE ... IF NOT EXISTS`), so the pipeline is **idempotent**: running it twice gives the same result (500 rows in the fact table both times).
- The job has a daily schedule and failure notifications.
- The data quality gate is the last task. A failed check marks the job as failed.

An **Airflow DAG** in `airflow/` can trigger this job. Airflow is not required here, because Databricks Workflows already handles scheduling, quality gate and alerts. It was added as a learning exercise (see `airflow/README.md`).

## API

A FastAPI service in `api/` serves the gold marts as JSON, reading live from a Databricks SQL warehouse. It runs in a Docker container and has its own unit tests. See [`api/README.md`](api/README.md).

| Endpoint | Returns |
|---|---|
| `GET /kpis/monthly-balance` | Net balance per month |
| `GET /kpis/failure-rate?category=` | Failure rate per category |
| `GET /kpis/monthly-category?year=&month=` | Completed amount per month and category |

Queries are parameterized and inputs are validated. The token is read from an environment variable and is never in the code or in the Docker image.

## Repository structure

```text
notebooks/   Databricks notebooks, numbered in execution order (01 to 12)
sql/         SQL files for objects created outside notebooks
src/         Business rule functions (pure Python)
tests/       pytest unit tests for src/
airflow/     Airflow DAG that triggers the Databricks job (learning exercise)
api/         FastAPI service that serves the gold marts, with Dockerfile and tests
powerbi/     Power BI report documentation: data model, DAX measures and screenshots
.github/     GitHub Actions workflow that runs the unit tests and the API tests on every push
```

## How to run

1. Create a free [Databricks Free Edition](https://www.databricks.com/learn/free-edition) workspace.
2. Clone this repository as a Git folder.
3. Run the notebooks in numeric order, or create a job with one task per notebook (see Orchestration above). Notebooks `07` to `10` are analyses and exercises and are not part of the job.
4. Create the materialized view from `sql/` using the SQL Editor (it needs a SQL warehouse).
5. To run the unit tests, run `12_run_unit_tests`, or run `python -m pytest tests` locally.
6. Optional: rebuild the Power BI report following `powerbi/README.md`.
7. Optional: run the API following `api/README.md`.

## Notes

- **Materialized view runs outside notebooks.** Materialized views require a SQL warehouse. The notebooks in this project run on serverless general compute (Databricks Free Edition), which returns `MV_NOT_ENABLED_ON_SERVERLESS_GENERIC_COMPUTE`. For that reason, the view is created from the SQL Editor, and its code is versioned in `sql/`.
- **Scheduling is owned by Databricks Workflows.** The Airflow DAG only triggers the job and exists as a learning exercise.
- **Write-then-audit design.** The pipeline writes the gold tables first and audits them afterwards. If a check fails, the job stops and alerts, but the tables were already written. A write-audit-publish pattern would avoid that.
- **Partial month.** October covers only 2026-10-01 to 2026-10-11, so it should not be compared directly with September.

## Roadmap

- [x] pytest and CI with GitHub Actions
- [x] Orchestration with Databricks Workflows and Airflow
- [x] Power BI dashboard
- [x] Docker and FastAPI
