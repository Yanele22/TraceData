import os
import sqlite3
import pandas as pd
import pytest
from src.transform.clean_data import clean_and_transform_data
from src.load.db_loader import load_data_to_db, create_database_schema

@pytest.fixture
def sample_raw_csv(tmp_path):
    """
    Creates a temporary raw CSV file with valid and invalid transaction rows.
    """
    raw_dir = tmp_path / "data" / "raw"
    raw_dir.mkdir(parents=True)
    raw_csv = raw_dir / "test_transactions.csv"

    data = (
        "transaction_id,account_id,timestamp,amount,merchant,location,device_id,status\n"
        "TX-001,ACC-100,2026-08-14 02:15:00,1850.00,FastPay,Cape Town,dev-123 ,COMPLETED\n"
        "TX-001,ACC-100,2026-08-14 02:15:00,1850.00,FastPay,Cape Town,dev-123 ,COMPLETED\n"  # Duplicate ID
        "TX-002,ACC-101,2026-08-14 03:00:00,-50.00,Office Store,Johannesburg,DEV-456,FAILED\n"  # Invalid negative amount
    )
    raw_csv.write_text(data, encoding="utf-8")
    return str(raw_csv)

def test_clean_and_transform_data(sample_raw_csv, tmp_path):
    """
    Tests that clean_and_transform_data properly removes duplicates,
    filters negative amounts, cleans string formatting, and engineers features.
    """
    output_csv = str(tmp_path / "data" / "processed" / "clean_transactions.csv")

    clean_and_transform_data(sample_raw_csv, output_csv)

    assert os.path.exists(output_csv)

    df = pd.read_csv(output_csv)

    # 1. Verify duplicates were dropped (from 3 rows to 1 valid row)
    assert len(df) == 1

    # 2. Verify negative amount row was filtered out
    assert df.iloc[0]["transaction_id"] == "TX-001"
    assert df.iloc[0]["amount"] == 1850.00

    # 3. Verify string cleaning (device_id trimmed and converted to uppercase)
    assert df.iloc[0]["device_id"] == "DEV-123"

    # 4. Verify engineered features exist
    assert "tx_hour" in df.columns
    assert "day_of_week" in df.columns
    assert df.iloc[0]["tx_hour"] == 2

def test_load_data_to_db(tmp_path):
    """
    Tests loading clean CSV data into an in-memory SQLite database instance.
    """
    # Create sample clean CSV
    clean_csv = str(tmp_path / "clean.csv")
    df_sample = pd.DataFrame([{
        "transaction_id": "TX-TEST-01",
        "account_id": "ACC-999",
        "timestamp": "2026-08-14 02:30:00",
        "amount": 1900.0,
        "merchant": "FastPay Global",
        "location": "Durban",
        "device_id": "DEV-777",
        "status": "COMPLETED",
        "tx_hour": 2,
        "day_of_week": "Friday"
    }])
    df_sample.to_csv(clean_csv, index=False)

    db_file = str(tmp_path / "test_tracedata.db")

    # Load into test DB
    load_data_to_db(clean_csv, db_file)

    # Query test DB to confirm insertion
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM transactions WHERE transaction_id = 'TX-TEST-01'")
    count = cursor.fetchone()[0]
    conn.close()

    assert count == 1