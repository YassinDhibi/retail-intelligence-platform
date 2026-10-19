from __future__ import annotations

import logging
import os
import re
import csv
import subprocess
import tempfile
from typing import Any
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote_plus

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.engine import Engine
except ImportError:
    create_engine = None
    text = None
    Engine = Any

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
RAW_SCHEMA = "raw"
DEFAULT_PSQL_PATH = Path("C:/Program Files/PostgreSQL/18/bin/psql.exe")

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class PostgresConfig:
    host: str
    port: str
    database: str
    user: str
    password: str

    @classmethod
    def from_env(cls) -> "PostgresConfig":
        load_local_env(PROJECT_ROOT / ".env")

        config = cls(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            database=os.getenv("POSTGRES_DB", "retail_warehouse"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", ""),
        )

        if not config.password:
            raise ValueError(
                "POSTGRES_PASSWORD is missing. Create a local .env file from .env.example "
                "or set the variable in your shell."
            )

        return config

    def sqlalchemy_url(self) -> str:
        user = quote_plus(self.user)
        password = quote_plus(self.password)
        host = self.host
        port = self.port
        database = self.database
        driver = get_postgres_driver()
        return f"postgresql+{driver}://{user}:{password}@{host}:{port}/{database}"


def load_local_env(env_path: Path) -> None:
    if load_dotenv is not None:
        load_dotenv(env_path)
        return

    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def get_postgres_driver() -> str:
    try:
        import psycopg2  # noqa: F401

        return "psycopg2"
    except ImportError:
        try:
            import psycopg  # noqa: F401

            return "psycopg"
        except ImportError as exc:
            raise ImportError(
                "No PostgreSQL driver found. Install psycopg2-binary or psycopg."
            ) from exc


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def normalize_table_name(csv_path: Path) -> str:
    table_name = csv_path.stem.lower()
    table_name = re.sub(r"[^a-z0-9_]+", "_", table_name)
    table_name = re.sub(r"_+", "_", table_name).strip("_")

    if not table_name:
        raise ValueError(f"Could not derive a table name from {csv_path.name}")

    if table_name[0].isdigit():
        table_name = f"csv_{table_name}"

    return table_name


def discover_csv_files(data_dir: Path = PROCESSED_DATA_DIR) -> list[Path]:
    if not data_dir.exists():
        raise FileNotFoundError(f"Processed data directory does not exist: {data_dir}")

    csv_files = sorted(path for path in data_dir.glob("*.csv") if path.is_file())
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {data_dir}")

    return csv_files


def create_postgres_engine(config: PostgresConfig) -> Engine:
    if create_engine is None:
        raise ImportError("SQLAlchemy is not installed.")

    return create_engine(config.sqlalchemy_url(), pool_pre_ping=True)


def ensure_schema_exists(engine: Engine, schema: str = RAW_SCHEMA) -> None:
    if text is None:
        raise ImportError("SQLAlchemy is not installed.")

    with engine.begin() as connection:
        connection.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))


def load_csv_to_postgres(csv_path: Path, engine: Engine, schema: str = RAW_SCHEMA) -> None:
    if pd is None:
        raise ImportError("pandas is not installed.")

    table_name = normalize_table_name(csv_path)
    LOGGER.info("Loading %s into %s.%s", csv_path.name, schema, table_name)

    try:
        dataframe = pd.read_csv(csv_path)
        if dataframe.empty:
            LOGGER.warning("Skipping %s because it has no rows", csv_path.name)
            return

        dataframe.to_sql(
            name=table_name,
            con=engine,
            schema=schema,
            if_exists="replace",
            index=False,
            chunksize=1_000,
            method="multi",
        )
        LOGGER.info(
            "Loaded %s rows and %s columns into %s.%s",
            f"{len(dataframe):,}",
            len(dataframe.columns),
            schema,
            table_name,
        )
    except Exception:
        LOGGER.exception("Failed to load %s", csv_path)
        raise


def load_processed_csvs() -> None:
    config = PostgresConfig.from_env()
    csv_files = discover_csv_files()

    LOGGER.info("Found %s CSV files in %s", len(csv_files), PROCESSED_DATA_DIR)

    if pd is not None and create_engine is not None:
        engine = create_postgres_engine(config)
        ensure_schema_exists(engine)

        for csv_path in csv_files:
            load_csv_to_postgres(csv_path, engine)
    else:
        LOGGER.warning(
            "pandas and SQLAlchemy are not both available. Falling back to psql COPY "
            "for raw-schema loading."
        )
        load_csvs_with_psql(csv_files, config)

    LOGGER.info("Finished loading cleaned CSV files into PostgreSQL schema: %s", RAW_SCHEMA)


def normalize_column_name(column_name: str, position: int) -> str:
    column = column_name.strip().lower()
    column = re.sub(r"[^a-z0-9_]+", "_", column)
    column = re.sub(r"_+", "_", column).strip("_")

    if not column:
        column = f"column_{position}"

    if column[0].isdigit():
        column = f"col_{column}"

    return column


def find_psql_path() -> Path:
    configured_path = os.getenv("PSQL_PATH")
    if configured_path:
        path = Path(configured_path)
        if path.exists():
            return path

    if DEFAULT_PSQL_PATH.exists():
        return DEFAULT_PSQL_PATH

    return Path("psql")


def run_psql(config: PostgresConfig, sql: str) -> None:
    env = os.environ.copy()
    env["PGPASSWORD"] = config.password
    command = [
        str(find_psql_path()),
        "-h",
        config.host,
        "-p",
        str(config.port),
        "-U",
        config.user,
        "-d",
        config.database,
        "-v",
        "ON_ERROR_STOP=1",
        "-c",
        sql,
    ]
    subprocess.run(command, env=env, check=True)


def create_raw_table_from_csv_header(csv_path: Path, table_name: str, config: PostgresConfig) -> list[str]:
    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.reader(file)
        header = next(reader)

    columns = [normalize_column_name(column, index + 1) for index, column in enumerate(header)]
    column_definitions = ", ".join(f'"{column}" text' for column in columns)

    sql = f'DROP TABLE IF EXISTS "{RAW_SCHEMA}"."{table_name}"; '
    sql += f'CREATE TABLE "{RAW_SCHEMA}"."{table_name}" ({column_definitions});'
    run_psql(config, sql)

    return columns


def copy_csv_with_normalized_header(
    csv_path: Path,
    table_name: str,
    columns: list[str],
    config: PostgresConfig,
) -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".csv", encoding="utf-8", newline="", delete=False) as temp_file:
        temp_path = Path(temp_file.name)
        writer = csv.writer(temp_file)
        writer.writerow(columns)

        with csv_path.open("r", encoding="utf-8-sig", newline="") as source_file:
            reader = csv.reader(source_file)
            next(reader)
            writer.writerows(reader)

    try:
        copy_sql = (
            f'\\copy "{RAW_SCHEMA}"."{table_name}" '
            f'FROM \'{temp_path.as_posix()}\' WITH (FORMAT csv, HEADER true)'
        )
        run_psql(config, copy_sql)
    finally:
        temp_path.unlink(missing_ok=True)


def load_csvs_with_psql(csv_files: list[Path], config: PostgresConfig) -> None:
    run_psql(config, f'CREATE SCHEMA IF NOT EXISTS "{RAW_SCHEMA}";')

    for csv_path in csv_files:
        table_name = normalize_table_name(csv_path)
        LOGGER.info("Loading %s into %s.%s with psql COPY", csv_path.name, RAW_SCHEMA, table_name)
        columns = create_raw_table_from_csv_header(csv_path, table_name, config)
        copy_csv_with_normalized_header(csv_path, table_name, columns, config)
        LOGGER.info("Loaded %s into %s.%s", csv_path.name, RAW_SCHEMA, table_name)


def main() -> None:
    configure_logging()
    try:
        load_processed_csvs()
    except Exception as exc:
        LOGGER.error("ETL pipeline failed: %s", exc)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
