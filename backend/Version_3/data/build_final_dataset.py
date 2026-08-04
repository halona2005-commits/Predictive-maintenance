import pandas as pd
import glob
import os

# Folder containing Excel files
DATA_FOLDER = r"D:\Predictive-maintenance\backend\Version-3\data"

# Read all Excel files
excel_files = glob.glob(os.path.join(DATA_FOLDER, "*.xlsx"))

if len(excel_files) == 0:
    print("❌ No Excel files found.")
    exit()

print("=" * 60)
print("FOUND FILES")
print("=" * 60)

for file in excel_files:
    print(os.path.basename(file))

dfs = []

for file in excel_files:
    df = pd.read_excel(file)
    dfs.append(df)

# Merge everything
merged = pd.concat(dfs, ignore_index=True)

# Remove duplicate rows if any
merged = merged.drop_duplicates()

# Sort by timestamp
merged["timestamp"] = pd.to_datetime(merged["timestamp"])
merged = merged.sort_values("timestamp").reset_index(drop=True)

print("\nTotal rows:", len(merged))
print("Columns:")
print(list(merged.columns))

# Save intermediate dataset
merged.to_csv("merged_dataset.csv", index=False)

print("\n✅ merged_dataset.csv created successfully")