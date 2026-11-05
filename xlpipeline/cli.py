import argparse
from pathlib import Path
import pandas as pd

from .db import *

def main(argv: list[str] | None = None) -> int:
    """Execute the XLpipeline CLI application.

    Args:
        argv: Optional list of command-line arguments. Defaults to sys.argv[1:].

    Returns:
        Exit code (0 for success, non-zero for failure).
    """

    parser = argparse.ArgumentParser(
        prog="xlpipeline",
        description="Read Excel files into a postgres database.",
    )
    parser.add_argument("excel_file", type=Path, help="Path to the Excel file to read")
    parser.add_argument(
        "--target-table", type=str, default=None, 
        help="Name of the target table in the database. If not provided, the table name " \
        "will be derived from the Excel file name."
    )
    args = parser.parse_args(argv)

    # Initialize connection
    conn = init_db_connection()

    # Inspect target table
    target_table = args.target_table if args.target_table else args.excel_file.stem
    table_df = inspect_target_table(conn, target_table)
    if table_df.empty:
        print(f"Table '{target_table}' is empty or does not exist.")
        print(f"Creating table '{target_table}' and inserting data from '{args.excel_file}'...")

    # Close Connection
    conn.close()

    return 0