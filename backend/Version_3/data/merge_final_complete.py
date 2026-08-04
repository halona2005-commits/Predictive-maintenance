import pandas as pd

print("=" * 60)
print("LOADING DATASETS")
print("=" * 60)

# Load datasets
old_df = pd.read_csv("final_dataset_complete.csv")
new_df = pd.read_csv("final_dataset_v3.csv")

print("Old Dataset :", old_df.shape)
print("New Dataset :", new_df.shape)

# --------------------------------------------------
# Columns required for training
# --------------------------------------------------

required_columns = [
    "ground_truth",

    "cpu_percent",
    "memory_percent",
    "memory_available_mb",
    "disk_write_mbps",

    "z_cpu",
    "z_mem",
    "z_memavl",
    "z_disk",

    "rolling_mean_cpu",
    "cpu_rate_of_change",
    "mem_drop_rate",
    "disk_burst_flag",

    "pem_score",
    "pem_status",

    "md_score",
    "md_status",

    "fault_type",
    "severity_level"
]

# Keep only columns that exist
old_df = old_df[[c for c in required_columns if c in old_df.columns]]
new_df = new_df[[c for c in required_columns if c in new_df.columns]]

# --------------------------------------------------
# Merge
# --------------------------------------------------

merged = pd.concat([old_df, new_df], ignore_index=True)

# Remove duplicates
merged = merged.drop_duplicates()

print("\nMerged Shape :", merged.shape)

print("\nMissing Values")
print(merged.isnull().sum())

print("\nGround Truth Distribution")
print(merged["ground_truth"].value_counts())

# Save
merged.to_csv("final_dataset_complete_v3.csv", index=False)

print("\n✅ final_dataset_complete_v3.csv created successfully")
