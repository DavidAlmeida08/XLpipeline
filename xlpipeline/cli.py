import argparse
from pathlib import Path
import pandas as pd

from .db import *
from .metrics import *

def main(argv: list[str] | None = None) -> int:
    """Execute the XLpipeline CLI application.

    Args:
        argv: Optional list of command-line arguments. Defaults to sys.argv[1:].

    Returns:
        Exit code (0 for success, non-zero for failure).
    """

    # Set up argument parser
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
    parser.add_argument("--metrics", action="store_true", help="Enable detailed output")
    args = parser.parse_args(argv)

    #Validate Excel file path
    if not args.excel_file.exists() or not args.excel_file.is_file():
        print(f"Error: The specified Excel file '{args.excel_file}' does not exist")
        return 1
    if args.excel_file.suffix.lower() not in {".xls", ".xlsx"}:
        print(f"Error: The specified file '{args.excel_file}' is not a valid Excel file")
        return 1

    # Initialize connection
    conn = init_db_connection()

    # Inspect target table
    target_table = args.target_table if args.target_table else args.excel_file.stem
    excel_data = pd.read_excel(args.excel_file)
    postgres_df = inspect_target_table(conn, target_table)

    # Metrics
    if args.metrics:
        benchmark_pipeline(conn, args.excel_file)
        return 0

    if postgres_df is None:
        print(f"Table '{target_table}' does not exist.")
        if not proceed_operation(f"create table '{target_table}' and insert data from '{args.excel_file}'"):
            print("Operation cancelled.")
            conn.close()
            return 1
        print(f"Creating table '{target_table}' and inserting data...")
    else: 
        if "is_active" in postgres_df.columns:
            convert_is_active(postgres_df, excel_data)
        print(f"Table '{target_table}' found. Appending data...")

    # Load into database and confirm sucess
    success = load_dataframe_to_table(conn, target_table, excel_data)
    conn.close()
    return 0 if success else 1


def proceed_operation(operation_name: str) -> bool:
    """Prompt the user to confirm whether to proceed with the operation.

    Returns:
        bool: True if the user confirms, False otherwise.
    """
    while True:
        response = input(f"Do you want to proceed with {operation_name}? (y/n): ").strip().lower()
        if response in {"y", "yes"}:
            return True
        elif response in {"n", "no"}:
            return False
        else:
            print("Invalid input. Please enter 'y' or 'n'.")


def convert_is_active(postgres_df: pd.DataFrame, excel_data: pd.DataFrame) -> None:
    """Convert 'is_active' to float if the existing database column is numeric.

    Args:
        postgres_df: DataFrame representing the existing PostgreSQL table schema.
        excel_data: DataFrame containing the Excel data to be inserted.
    """
    if "is_active" in excel_data.columns:
        if postgres_df["is_active"].dtype in ["float64", "float32", "int64", "int32"]:
            excel_data["is_active"] = excel_data["is_active"].astype(float)
    