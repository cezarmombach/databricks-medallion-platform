# Method: Databricks SQL connector wrapped in a small helper
# Objective: Run a parameterized SQL query and return the rows as a list of dicts.

import os

from databricks import sql
from dotenv import load_dotenv

# Read variables from the .env file into the process environment.
# It does nothing when the file is absent, which is what we want inside Docker.
load_dotenv()


def run_query(query: str, parameters: dict | None = None) -> list[dict]:
    # os.environ[...] raises KeyError if a variable is missing: fail fast
    connection = sql.connect(
        server_hostname=os.environ["DATABRICKS_SERVER_HOSTNAME"],
        http_path=os.environ["DATABRICKS_HTTP_PATH"],
        access_token=os.environ["DATABRICKS_TOKEN"],
    )
    try:
        with connection.cursor() as cursor:
            # Values travel separately from the SQL text (named markers like :category)
            cursor.execute(query, parameters)
            rows = cursor.fetchall()
            return [row.asDict() for row in rows]
    finally:
        connection.close()