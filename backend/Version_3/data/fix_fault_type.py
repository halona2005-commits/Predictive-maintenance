import pandas as pd

# Load the merged dataset
df = pd.read_csv("final_dataset_complete_v3.csv")

# Replace missing values
df["fault_type"] = df["fault_type"].fillna("UNKNOWN")

# Save the updated dataset
df.to_csv("final_dataset_complete_v3.csv", index=False)

print("\nMissing Values After Fix:")
print(df.isnull().sum())

print("\n✅ Dataset updated successfully!")