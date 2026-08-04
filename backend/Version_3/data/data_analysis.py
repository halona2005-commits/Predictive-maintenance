import pandas as pd

# Change the path if required
df = pd.read_csv("final_dataset_complete.csv")

print("=" * 60)
print("DATASET ANALYSIS")
print("=" * 60)

print("\nTotal Samples")
print(len(df))

print("\nNormal Samples")
print(len(df[df["ground_truth"] == 0]))

print("\nAnomaly Samples")
print(len(df[df["ground_truth"] == 1]))

# -------------------------------------------------------
# Feature Statistics
# -------------------------------------------------------

features = [
    "cpu_percent",
    "memory_percent",
    "memory_available_mb",
    "disk_write_mbps"
]

for feature in features:

    print("\n" + "=" * 50)
    print(feature.upper())
    print("=" * 50)

    normal = df[df["ground_truth"] == 0][feature]
    anomaly = df[df["ground_truth"] == 1][feature]

    print("\nNORMAL")

    print(f"Mean : {normal.mean():.2f}")
    print(f"Std  : {normal.std():.2f}")
    print(f"Min  : {normal.min():.2f}")
    print(f"Max  : {normal.max():.2f}")

    print("\nANOMALY")

    print(f"Mean : {anomaly.mean():.2f}")
    print(f"Std  : {anomaly.std():.2f}")
    print(f"Min  : {anomaly.min():.2f}")
    print(f"Max  : {anomaly.max():.2f}")

# -------------------------------------------------------
# Memory Distribution
# -------------------------------------------------------

print("\n")
print("=" * 60)
print("MEMORY DISTRIBUTION")
print("=" * 60)

levels = [60, 65, 70, 75, 80, 85, 90]

for level in levels:

    normal = len(
        df[
            (df["ground_truth"] == 0) &
            (df["memory_percent"] > level)
        ]
    )

    anomaly = len(
        df[
            (df["ground_truth"] == 1) &
            (df["memory_percent"] > level)
        ]
    )

    total = normal + anomaly

    if total == 0:
        continue

    anomaly_percentage = anomaly / total * 100

    print(f"\nMemory > {level}%")

    print(f"Normal  : {normal}")
    print(f"Anomaly : {anomaly}")

    print(f"Anomaly Probability : {anomaly_percentage:.2f}%")

# -------------------------------------------------------
# CPU Distribution
# -------------------------------------------------------

print("\n")
print("=" * 60)
print("CPU DISTRIBUTION")
print("=" * 60)

levels = [20, 40, 60, 80]

for level in levels:

    normal = len(
        df[
            (df["ground_truth"] == 0) &
            (df["cpu_percent"] > level)
        ]
    )

    anomaly = len(
        df[
            (df["ground_truth"] == 1) &
            (df["cpu_percent"] > level)
        ]
    )

    total = normal + anomaly

    if total == 0:
        continue

    anomaly_percentage = anomaly / total * 100

    print(f"\nCPU > {level}%")

    print(f"Normal  : {normal}")
    print(f"Anomaly : {anomaly}")

    print(f"Anomaly Probability : {anomaly_percentage:.2f}%")

# -------------------------------------------------------
# Disk Distribution
# -------------------------------------------------------

print("\n")
print("=" * 60)
print("DISK DISTRIBUTION")
print("=" * 60)

levels = [1, 5, 10, 20]

for level in levels:

    normal = len(
        df[
            (df["ground_truth"] == 0) &
            (df["disk_write_mbps"] > level)
        ]
    )

    anomaly = len(
        df[
            (df["ground_truth"] == 1) &
            (df["disk_write_mbps"] > level)
        ]
    )

    total = normal + anomaly

    if total == 0:
        continue

    anomaly_percentage = anomaly / total * 100

    print(f"\nDisk > {level} MB/s")

    print(f"Normal  : {normal}")
    print(f"Anomaly : {anomaly}")

    print(f"Anomaly Probability : {anomaly_percentage:.2f}%")

print("\n")
print("=" * 60)
print("ANALYSIS COMPLETE")
print("=" * 60)