from __future__ import annotations

from datetime import datetime
from pathlib import Path

from airflow import DAG
from airflow.operators.bash import BashOperator


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT_POSIX = PROJECT_ROOT.as_posix()

default_args = {
    "owner": "retail-intelligence-platform",
    "depends_on_past": False,
}


def project_python_command(script_path: str) -> str:
    return f"cd {PROJECT_ROOT_POSIX} && python {script_path}"


def project_psql_command(sql_path: str) -> str:
    return (
        f"cd {PROJECT_ROOT_POSIX} && "
        "PGPASSWORD=${POSTGRES_PASSWORD:-postgres} "
        "psql -h ${POSTGRES_HOST:-localhost} "
        "-p ${POSTGRES_PORT:-5432} "
        "-U ${POSTGRES_USER:-postgres} "
        "-d ${POSTGRES_DB:-retail_warehouse} "
        f"-v ON_ERROR_STOP=1 -f {sql_path}"
    )


with DAG(
    dag_id="retail_intelligence_pipeline",
    description="Clean retail CSV files, refresh PostgreSQL models, and train forecasting.",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["retail", "postgres", "analytics", "ml"],
) as dag:
    clean_data = BashOperator(
        task_id="clean_data",
        bash_command=project_python_command("src/transform.py"),
    )

    load_raw_tables = BashOperator(
        task_id="load_raw_tables",
        bash_command=project_python_command("src/load_to_postgres.py"),
    )

    refresh_staging = BashOperator(
        task_id="refresh_staging",
        bash_command=project_psql_command("sql/02_create_staging_tables.sql"),
    )

    refresh_warehouse = BashOperator(
        task_id="refresh_warehouse",
        bash_command=project_psql_command("sql/03_create_warehouse_tables.sql"),
    )

    refresh_marts = BashOperator(
        task_id="refresh_marts",
        bash_command=project_psql_command("sql/04_create_marts.sql"),
    )

    train_forecasting_model = BashOperator(
        task_id="train_forecasting_model",
        bash_command=project_python_command("ml/train_forecasting_model.py"),
    )

    clean_data >> load_raw_tables >> refresh_staging >> refresh_warehouse >> refresh_marts >> train_forecasting_model
