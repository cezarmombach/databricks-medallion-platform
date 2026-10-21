# Airflow

Local Airflow (Docker Compose) that triggers the Databricks job `medallion_pipeline`.

## Files

- `dags/trigger_medallion_pipeline.py`: DAG that runs the Databricks job and waits for it to finish.

## How to run locally

1. Download the official Docker Compose file for your Airflow version (3.3.2 was used here):
   `curl.exe -LfO "https://airflow.apache.org/docs/apache-airflow/3.3.2/docker-compose.yaml"`
2. Create the folders `dags`, `logs`, `plugins` and `config`, and a `.env` file with:
```text
   AIRFLOW_UID=50000
   _PIP_ADDITIONAL_REQUIREMENTS=apache-airflow-providers-databricks
```
3. Run `docker compose up airflow-init`, then `docker compose up`.
4. Open http://localhost:8080 and create a Connection named `databricks_default` (type Databricks) with your workspace host and a personal access token.
5. Copy the DAG into `dags/`, set `DATABRICKS_JOB_ID`, and trigger it from the UI.

> Never commit tokens. The token is typed only in the Airflow Connections screen.
