from pathlib import Path
import time

import pandas as pd
from sqlalchemy import Connection, Engine

from .config import METRICS_TABLE_NAME, EXCEL_PATH
from .db import load_dataframe_to_table


def benchmark_pipeline(conn: Connection | Engine) -> dict[str, float]:
    """Benchmark Excel file reading and database insertion performance.

    Measures parse time, database loading time, total wall-clock time,
    and throughput in rows per second, printing a summary report.

    Args:
        conn: Active database connection or engine.
        excel_path: Path to the Excel file to read and benchmark.

    Returns:
        dict[str, float]: Dictionary containing execution times and throughput metrics.
    """
    total_start = time.perf_counter()

    # 1. Measure Excel reading time
    t0 = time.perf_counter()
    df = pd.read_excel(EXCEL_PATH)
    t_parse = time.perf_counter() - t0

    num_rows = len(df)
    num_cols = len(df.columns)

    # 2. Measure database insertion time
    t0 = time.perf_counter()
    load_dataframe_to_table(conn, METRICS_TABLE_NAME, df, chunksize=1000)
    t_db = time.perf_counter() - t0

    total_time = time.perf_counter() - total_start

    # Calculate throughput metrics
    throughput_parse = num_rows / t_parse if t_parse > 0 else 0.0
    throughput_db = num_rows / t_db if t_db > 0 else 0.0
    throughput = num_rows / total_time if total_time > 0 else 0.0

    print("\n--- Performance Report ---")
    print(f"File: {EXCEL_PATH.name} ({num_rows} rows, {num_cols} columns)")
    print(f"Excel Parse Time:    {t_parse:.3f} s ({throughput_parse:.1f} rows/s)")
    print(f"Database Load Time:  {t_db:.3f} s ({throughput_db:.1f} rows/s)")
    print(f"Total Time:          {total_time:.3f} s")
    print(f"Overall Throughput:  {throughput:.1f} rows/s")
    print("--------------------------\n")

    return {
        "rows": float(num_rows),
        "parse_time_s": t_parse,
        "parse_rows_per_second": throughput_parse,
        "db_time_s": t_db,
        "db_rows_per_second": throughput_db,
        "total_time_s": total_time,
        "rows_per_second": throughput,
    }
