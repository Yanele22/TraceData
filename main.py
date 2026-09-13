import sys
import os

from src.extract.generate_data import rows  # Triggers raw generation
from src.transform.clean_data import clean_and_transform_data
from src.load.db_loader import load_data_to_db
from src.detective.investigate import run_forensic_investigation

RAW_PATH = "data/raw/transactions.csv"
PROCESSED_PATH = "data/processed/clean_transactions.csv"
DB_PATH = "data/processed/tracedata.db"

def run_pipeline():
    """
    Orchestrates the end-to-end TraceData pipeline execution.
    """
    print("=======================================================")
    print("🚀 TRACEDATA PIPELINE ORCHESTRATOR — CASE #001 STARTING")
    print("=======================================================\n")

    # Stage 1: Data Extraction / Generation
    print("-------------------------------------------------------")
    print("STAGE 1: EXTRACTING & GENERATING RAW EVIDENCE")
    print("-------------------------------------------------------")
    # Execute generator script dynamically
    os.system(f"{sys.executable} src/extract/generate_data.py")

    # Stage 2: Data Cleaning & Transformation
    print("\n-------------------------------------------------------")
    print("STAGE 2: TRANSFORMING & CLEANING DATA")
    print("-------------------------------------------------------")
    clean_and_transform_data(input_path=RAW_PATH, output_path=PROCESSED_PATH)

    # Stage 3: Database Storage & Loading
    print("\n-------------------------------------------------------")
    print("STAGE 3: LOADING DATA INTO SQL DATABASE VAULT")
    print("-------------------------------------------------------")
    load_data_to_db(csv_path=PROCESSED_PATH, db_path=DB_PATH)

    # Stage 4: Detective Engine Investigation
    print("\n-------------------------------------------------------")
    print("STAGE 4: RUNNING FORENSIC DETECTIVE ENGINE")
    print("-------------------------------------------------------")
    run_forensic_investigation(db_path=DB_PATH)

    print("\n=======================================================")
    print("✅ TRACEDATA PIPELINE EXECUTION COMPLETE")
    print("=======================================================")

if __name__ == "__main__":
    run_pipeline()