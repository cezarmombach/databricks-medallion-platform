# Method: Airflow DAG with DatabricksRunNowOperator
# Objective: Trigger the existing Databricks job "medallion_pipeline" and wait for it to finish.

from datetime import datetime

from airflow.sdk import DAG, task
from airflow.providers.databricks.operators.databricks import DatabricksRunNowOperator

# Job ID of "medallion_pipeline" (Databricks > Jobs > the job > right panel > Job ID)
DATABRICKS_JOB_ID = 1100837230764299 

with DAG(
    dag_id="trigger_medallion_pipeline",
    description="Runs the Databricks medallion job from Airflow",
    start_date=datetime(2026, 10, 1),
    schedule=None,       # manual trigger only (the Databricks job already has its own schedule)
    catchup=False,       # do not create runs for past dates
    tags=["databricks", "medallion"],
) as dag:

    run_medallion_job = DatabricksRunNowOperator(
        task_id="run_medallion_job",
        databricks_conn_id="databricks_default",  # the Connection we created in the UI
        job_id=DATABRICKS_JOB_ID,
    )

    @task
    def report_success():
        print("Databricks job finished successfully")

    run_medallion_job >> report_success()
