import os
import pandas as pd

def clean_and_transform_data(input_path: str, output_path: str):
    """
    Reads raw evidence transactions, performs data quality checks,
    transforms types, and outputs a clean dataset for database loading.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Raw data file not found at {input_path}")

    print(f"🔍 Reading raw data from '{input_path}'...")
    df = pd.read_csv(input_path)

    initial_row_count = len(df)

    # 1. Type Casting & Timestamp Parsing
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    # 2. Data Cleaning & Quality Rules
    # Drop exact duplicate transaction IDs
    df = df.drop_duplicates(subset=["transaction_id"])

    # Filter out invalid or negative transaction amounts
    df = df[df["amount"] > 0]

    # Clean string fields
    df["device_id"] = df["device_id"].str.strip().str.upper()
    df["location"] = df["location"].str.strip().title()
    df["merchant"] = df["merchant"].str.strip()

    # 3. Feature Engineering for Investigation
    # Extract hour and day of week to assist downstream forensic queries
    df["tx_hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.day_name()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"✅ Pipeline Clean Complete: {initial_row_count} raw rows -> {len(df)} processed rows saved to '{output_path}'")

if __name__ == "__main__":
    clean_and_transform_data(
        input_path="data/raw/transactions.csv",
        output_path="data/processed/clean_transactions.csv"
    )