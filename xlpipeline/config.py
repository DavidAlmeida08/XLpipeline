import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.example")

# Database credentials and connection parameters
DRIVER = "postgresql+psycopg2"

HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT") 
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Metrics config
METRICS_TABLE_NAME = "metrics"
EXCEL_PATH = "test.xlsx"