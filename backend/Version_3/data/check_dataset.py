import pandas as pd

df = pd.read_csv("final_dataset_complete_v3.csv")

print("Shape:", df.shape)
print("\nColumns:")
print(df.columns.tolist())

print("\nFirst 5 rows:")
print(df.head())