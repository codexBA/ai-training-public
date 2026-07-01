import os
import pyodbc
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    server = os.getenv("DB_SERVER", r"localhost\SQLEXPRESS")
    database = os.getenv("DB_NAME", "StateStatisticsDB")
    user = os.getenv("DB_USER", "")
    password = os.getenv("DB_PASSWORD", "")
    use_trusted = os.getenv("DB_TRUSTED_CONNECTION", "yes").lower() in ("yes", "true", "1")

    if use_trusted:
        connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;"
    else:
        connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={user};PWD={password};"
    
    conn = pyodbc.connect(connection_string)
    return conn
