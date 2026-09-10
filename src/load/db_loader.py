import os
import sqlite3
import pandas as pd

DB_PATH = "data/processed/tracedata.db"
CLEAN_DATA_PATH = "data/processed/clean_transactions.csv"

def create_database_schema(conn):
    """
    Creates the database table for transactions if it doesn't already exist.
    """
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            amount REAL NOT NULL,
            merchant TEXT NOT NULL,
            location TEXT NOT NULL,
            device_id TEXT NOT NULL,
            status TEXT NOT NULL,
            tx_hour INTEGER,
            day_of_week TEXT
        )
    """)
    conn.commit()
    print("✅ Database schema initialized ('transactions' table ready).")

def load_data_to_db(csv_path: str, db_path: str):
    """
    Loads cleaned CSV data into the local SQLite database vault.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Cleaned dataset missing at '{csv_path}'. Run clean_data.py first!")

    df = pd.read_csv(csv_path)

    # Establish connection
    conn = sqlite3.connect(db_path)
    
    # 1. Create table schema
    create_database_schema(conn)

    # 2. Insert cleaned data into SQL database
    df.to_sql("transactions", conn, if_exists="replace", index=False)
    
    # Verify record count
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM transactions")
    count = cursor.fetchone()[0]
    
    conn.close()
    print(f"✅ Successfully loaded {count} records into '{db_path}'!")

if __name__ == "__main__":
    load_data_to_db(CLEAN_DATA_PATH, DB_PATH)