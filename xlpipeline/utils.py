from pathlib import Path
import pandas as pd
from xlsx2csv import Xlsx2csv
import io


def get_excel_data(excel_path: Path) -> pd.DataFrame:
    """Convert excel's content to csv and read to a memory buffer for faster read times.
    
    Args:
       excel_path: Path to the target excel file.
       
    Returns:
        pd.DataFrame: DataFrame containing the file content contents.
    """

    with io.StringIO() as buffer:
        Xlsx2csv(str(excel_path), outputencoding="utf-8").convert(buffer)
        buffer.seek(0)
        return pd.read_csv(buffer)


def convert_is_active(postgres_df: pd.DataFrame, excel_data: pd.DataFrame) -> None:
    """Convert 'is_active' to float if the existing database column is numeric.

    Args:
        postgres_df: DataFrame representing the existing PostgreSQL table schema.
        excel_data: DataFrame containing the Excel data to be inserted.
    """
    if "is_active" in excel_data.columns:
        if postgres_df["is_active"].dtype in ["float64", "float32", "int64", "int32"]:
            excel_data["is_active"] = excel_data["is_active"].astype(float)

