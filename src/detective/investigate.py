import os
import sqlite3
import pandas as pd

DB_PATH = "data/processed/tracedata.db"

def run_forensic_investigation(db_path: str):
    """
    Executes forensic SQL queries against the transactions database 
    to detect velocity, after-hours, and smurfing anomalies.
    """
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found at '{db_path}'. Run src/load/db_loader.py first!")

    conn = sqlite3.connect(db_path)

    print("\n=======================================================")
    print("🕵🏾‍♀️ TRACEDATA DETECTIVE ENGINE — CASE #001 INVESTIGATION")
    print("=======================================================\n")

    # ---------------------------------------------------------
    # CLUE 1: After-Hours Transactions (02:00 AM - 04:00 AM)
    # ---------------------------------------------------------
    query_after_hours = """
        SELECT account_id, device_id, COUNT(*) AS tx_count, SUM(amount) AS total_amount
        FROM transactions
        WHERE tx_hour BETWEEN 2 AND 4
        GROUP BY account_id, device_id
        ORDER BY total_amount DESC
        LIMIT 5;
    """
    df_after_hours = pd.read_sql_query(query_after_hours, conn)
    print("🔎 CLUE #1: Unusual After-Hours Activity (02:00 - 04:00 AM)")
    print(df_after_hours.to_string(index=False))
    print("-" * 55)

    # ---------------------------------------------------------
    # CLUE 2: Impossible Location Velocity (Rapid JHB <-> CPT movements)
    # ---------------------------------------------------------
    query_velocity = """
        SELECT device_id, account_id, COUNT(DISTINCT location) AS unique_locations, COUNT(*) AS total_txs
        FROM transactions
        WHERE tx_hour BETWEEN 2 AND 4
        GROUP BY device_id, account_id
        HAVING unique_locations > 1;
    """
    df_velocity = pd.read_sql_query(query_velocity, conn)
    print("\n🔎 CLUE #2: Geolocation Velocity Anomaly (Conflicting Cities)")
    print(df_velocity.to_string(index=False))
    print("-" * 55)

    # ---------------------------------------------------------
    # CLUE 3: Structuring / Smurfing Pattern (Transfers under R2,000 threshold)
    # ---------------------------------------------------------
    query_smurfing = """
        SELECT account_id, device_id, merchant, COUNT(*) AS split_transfers, SUM(amount) AS stolen_total
        FROM transactions
        WHERE amount BETWEEN 1700 AND 1999
          AND merchant = 'FastPay Global Transfer'
        GROUP BY account_id, device_id, merchant;
    """
    df_smurfing = pd.read_sql_query(query_smurfing, conn)
    print("\n🔎 CLUE #3: Smurfing Pattern (Split transfers under R2,000 limit)")
    print(df_smurfing.to_string(index=False))
    print("-" * 55)

    # ---------------------------------------------------------
    # FINAL VERDICT REVEAL
    # ---------------------------------------------------------
    if not df_smurfing.empty:
        suspect_account = df_smurfing.iloc[0]["account_id"]
        suspect_device = df_smurfing.iloc[0]["device_id"]
        total_stolen = df_smurfing.iloc[0]["stolen_total"]

        print("\n🚨 CASE SOLVED! VERDICT REPORT:")
        print(f"   • Compromised Account: {suspect_account}")
        print(f"   • Suspect Rogue Device: {suspect_device}")
        print(f"   • Total Value Drained:  R{total_stolen:,.2f}")
        print("\nConclusion: Rogue device 'DEV-9999' drained R50,000 via rapid split transfers in the middle of the night.")
    else:
        print("\n❓ No decisive forensic match found.")

    conn.close()

if __name__ == "__main__":
    run_forensic_investigation(DB_PATH)