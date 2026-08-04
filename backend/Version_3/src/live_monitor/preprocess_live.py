"""
===========================================================
LIVE DATA PREPROCESSING
Version 3
===========================================================
"""

import pandas as pd
import joblib

# Files
LIVE_DATA = "../../data/live_data.csv"
OUTPUT = "../../data/processed_live_data.csv"
SCALER = "../../models/scaler.pkl"

# Read live data
df = pd.read_csv(LIVE_DATA)

print("=" * 60)
print("Live Data Preprocessing")
print("=" * 60)

print("Rows :", len(df))

# -----------------------------
# Remove duplicate rows
# -----------------------------

df = df.drop_duplicates()

# -----------------------------
# Fill missing values
# -----------------------------

df = df.ffill()
df = df.bfill()

# -----------------------------
# Columns used by collector
# -----------------------------

feature_columns = [
    "cpu_percent",
    "ram_percent",
    "ram_available_mb",
    "disk_percent",
    "disk_free_gb",
    "bytes_sent",
    "bytes_recv",
    "process_count"
]

# Load Version 2 scaler
scaler = joblib.load(SCALER)

# Scale
scaled = scaler.transform(df[feature_columns])

scaled_df = pd.DataFrame(
    scaled,
    columns=feature_columns
)

scaled_df.to_csv(
    OUTPUT,
    index=False
)

print("\nProcessed data saved to:")
print(OUTPUT)

print("\nDone.")