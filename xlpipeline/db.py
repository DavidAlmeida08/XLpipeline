from typing import Literal
import pandas as pd
from sqlalchemy import Connection, Engine, create_engine, text
from sqlalchemy.engine import URL

from .config import DRIVER, DB_NAME, DB_PASSWORD, DB_USER, HOST, PORT


def init_db_connection() -> Connection:
    """Initialize a connection to the PostgreSQL database using credentials from config.py.

    Returns:
        Connection: A SQLAlchemy Connection object.

    Raises:
        Exception: If connection to database fails.
    """
    try:
        engine = init_db_engine()
        conn = engine.connect()
        print("Database connection established successfully.")
        return conn

    except Exception as error:
        print(f"Error connecting to database: {error}")
        raise


def init_db_engine() -> Engine:
    """Initialize a SQLAlchemy Engine using credentials from config.py.

    Returns:
        Engine: An active SQLAlchemy engine instance.

    Raises:
        Exception: If the engine could not be initialized.
    """
    try:
        connection_url = URL.create(
            drivername=DRIVER,
            username=DB_USER,
            password=DB_PASSWORD,
            host=HOST,
            port=int(PORT) if PORT else 5432,
            database=DB_NAME,
        )
        engine = create_engine(connection_url, pool_pre_ping=True)
        return engine

    except Exception as error:
        print(f"Error initializing database engine: {error}")
        raise


def inspect_target_table(conn: Connection | Engine, table_name: str) -> pd.DataFrame:
    """Inspect the target table in the database.

    Args:
        conn: Active database connection or engine.
        table_name: Name of the target table to inspect.

    Returns:
        pd.DataFrame: DataFrame containing the table's contents, or None if the table does not exist.
    """
    try:
        df = pd.read_sql_query(text(f"SELECT * FROM {table_name};"), conn)
        return df

    except Exception as error:
        if hasattr(conn, "rollback"):
            conn.rollback()
        print(f"Error inspecting table {table_name} {':' + str(error.orig) if hasattr(error, 'orig') else ''}")
        return None


def load_dataframe_to_table(
    conn: Connection | Engine,
    table_name: str,
    df: pd.DataFrame,
    if_exists: Literal["append", "replace", "fail"] = "append",
    chunksize: int | None = 1000,
) -> bool:
    """Load a DataFrame into a PostgreSQL table (creates table if missing or appends if present).
    Args:
        conn: Active SQLAlchemy connection or engine.
        table_name: Name of the target table.
        df: DataFrame containing the records to insert.
        if_exists: Behavior if table exists ('append', 'replace', or 'fail'). Defaults to 'append'.
        chunksize: Number of rows to write at a time. Defaults to 1000.
    Returns:
        bool: True if operation succeeded, False otherwise.
    """
    if df is None or df.empty:
        print("Warning: DataFrame is empty. No records to load.")
        return False
    try:
        df.to_sql(
            table_name,
            conn,
            if_exists=if_exists,
            index=False,
            chunksize=chunksize,
            method="multi",
        )
        if hasattr(conn, "commit"):
            conn.commit()
        print(f"Successfully loaded {len(df)} rows into table '{table_name}'.")
        return True
    
    except Exception as error:
        if hasattr(conn, "rollback"):
            conn.rollback()
        err_msg = getattr(error, "orig", error)
        print(f"Error loading data into table '{table_name}': {err_msg}")
        return False
    
