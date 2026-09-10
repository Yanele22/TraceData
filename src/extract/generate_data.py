import csv
import os
import random
from datetime import datetime, timedelta

# Create output folder if it doesn't exist
os.makedirs("data/raw", exist_ok=True)

# Configuration for Case #001
TOTAL_NORMAL_TRANSACTIONS = 2000
START_DATE = datetime(2026, 8, 1)
LOCATIONS = ["Johannesburg", "Cape Town", "Durban", "Pretoria", "Gqeberha"]
DEVICES = [f"DEV-{i:04d}" for i in range(100, 150)]
MERCHANTS = ["AWS Cloud Services", "Office Supplies Co", "Uber SA", "Woolworths", "Takealot", "Bolt Food"]
ACCOUNTS = [f"ACC-{i:04d}" for i in range(1000, 1050)]

rows = []

# 1. Generate Legitimate Business Transactions
for i in range(1, TOTAL_NORMAL_TRANSACTIONS + 1):
    tx_id = f"TX-NORM-{i:05d}"
    account = random.choice(ACCOUNTS)
    
    # Random timestamp during August 2026 (business hours 08:00 - 18:00)
    day_offset = random.randint(0, 30)
    hour = random.randint(8, 18)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    tx_time = START_DATE + timedelta(days=day_offset, hours=hour, minutes=minute, seconds=second)
    
    amount = round(random.uniform(50.00, 4500.00), 2)
    merchant = random.choice(MERCHANTS)
    location = random.choice(LOCATIONS)
    device = random.choice(DEVICES)
    
    rows.append([tx_id, account, tx_time.strftime("%Y-%m-%d %H:%M:%S"), amount, merchant, location, device, "COMPLETED"])

# 2. Inject Anomaly Pattern: The R50,000 Midnight Drain
# Suspect steals R50,000 using 28 transactions (~R1,785 each, under R2,000 flag threshold)
SUSPECT_DEVICE = "DEV-9999"  # Rogue device signature
SUSPECT_ACCOUNT = "ACC-1042"  # Compromised internal account
ANOMALY_DATE = datetime(2026, 8, 14, 2, 15, 0) # 02:15 AM on August 14

stolen_total = 0
for i in range(1, 29):
    tx_id = f"TX-ANOM-{i:03d}"
    
    # Rapid sequence: transactions occurring every 15-45 seconds
    tx_time = ANOMALY_DATE + timedelta(seconds=i * random.randint(15, 45))
    
    # Amounts kept just under R2,000 threshold
    if i == 28:
        amount = round(50000.00 - stolen_total, 2)
    else:
        amount = round(random.uniform(1750.00, 1950.00), 2)
        stolen_total += amount
        
    merchant = "FastPay Global Transfer"
    
    # Impossible velocity: Alternating between Joburg and Cape Town within seconds
    location = "Cape Town" if i % 2 == 0 else "Johannesburg"
    
    rows.append([tx_id, SUSPECT_ACCOUNT, tx_time.strftime("%Y-%m-%d %H:%M:%S"), amount, merchant, location, SUSPECT_DEVICE, "COMPLETED"])

# Shuffle rows so anomalies are mixed into normal data chronologically
rows.sort(key=lambda x: x[2])

# Write to CSV
file_path = "data/raw/transactions.csv"
headers = ["transaction_id", "account_id", "timestamp", "amount", "merchant", "location", "device_id", "status"]

with open(file_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    writer.writerows(rows)

print(f"✅ Generated {len(rows)} raw transactions in '{file_path}'")