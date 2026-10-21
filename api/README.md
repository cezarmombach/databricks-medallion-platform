# KPI API

A small FastAPI service that serves the gold-layer marts of this project as JSON. It queries a Databricks SQL warehouse and runs in a Docker container.

## Endpoints

| Endpoint | Returns | Source |
|---|---|---|
| `GET /health` | `{"status": "ok"}` | n/a |
| `GET /kpis/monthly-balance` | Net balance per month (BR-02) | `mart_monthly_balance` |
| `GET /kpis/failure-rate?category=` | Failure rate per category (BR-03), optional filter | `mart_failure_rate_category` |
| `GET /kpis/monthly-category?year=&month=` | Completed amount per month and category (BR-01), optional filters | `mart_monthly_category` |

Interactive documentation is generated automatically at `/docs`.

## Design decisions

- **Parameterized queries:** user input never becomes part of the SQL text, which prevents SQL injection.
- **Input validation:** invalid values (for example `month=13`) are rejected by FastAPI with a 422 before reaching the database.
- **Safe errors:** if Databricks fails, the client receives a generic 503. The real error stays in the server log.
- **Secrets by environment variables:** the token is never in the code or in the image (`.dockerignore` excludes `.env`).

## Configuration

Copy `.env.example` to `.env` and fill in your values (the hostname without `https://`):

```text
DATABRICKS_SERVER_HOSTNAME=...
DATABRICKS_HTTP_PATH=...
DATABRICKS_TOKEN=...
```

Never commit the `.env` file.

## Run locally

```bash
python -m venv .venv
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Run with Docker

```bash
docker build -t medallion-api .
docker run --rm -p 8000:8000 --env-file .env medallion-api
```

## Tests

The tests replace the database with a fake, so they need neither Databricks nor a token:

```bash
pip install pytest httpx
python -m pytest tests -v
```

## Notes

- The first request can take a while: the Databricks Free Edition SQL warehouse starts on demand.
- The API is read-only and has no authentication. It is a learning project and should not be exposed to the internet as is.
