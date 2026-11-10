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
    excel_data = pd.read_excel(args.excel_file, index_col=0)
    postgres_df = inspect_target_table(conn, target_table)

    # Table is empty(inspect_target_table returns empty DataFrame if table does not exist)
    if postgres_df is None:
        print(f"Table '{target_table}' does not exist.")
        if not proceed_operation(f"create table '{target_table}' and insert data from '{args.excel_file}'"):
            print("Operation cancelled.")
            conn.close()
            return 1
        
        print(f"Creating table '{target_table}' and inserting data from '{args.excel_file}'...")
        if not create_table(conn, target_table, excel_data):
            conn.close()
            return 1
        return 0

    # Table exists
    print("Table found")
    if not update_table(conn, target_table, excel_data):
        conn.close()
        return 1
  
    # Close Connection
    conn.close()
    return 0


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
    