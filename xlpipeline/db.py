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
        pd.DataFrame: DataFrame containing the table's contents, or an empty DataFrame if the table does not exist.
    """
    try:
        df = pd.read_sql_query(text(f"SELECT * FROM {table_name};"), conn)
        return df

    except Exception as error:
        if hasattr(conn, "rollback"):
            conn.rollback()
        print(f"Error inspecting table {table_name} {':' + str(error.orig) if hasattr(error, 'orig') else ''}")

    return pd.DataFrame()
