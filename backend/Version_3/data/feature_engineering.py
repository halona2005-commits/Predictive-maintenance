import pandas as pd
import numpy as np
from scipy.spatial.distance import mahalanobis

# Load merged dataset
df = pd.read_csv("merged_dataset.csv")

# -------------------------
# Z-SCORE FEATURES
# -------------------------

df["z_cpu"] = (
    df["cpu_percent"] - df["cpu_percent"].mean()
) / df["cpu_percent"].std()

df["z_mem"] = (
    df["memory_percent"] - df["memory_percent"].mean()
) / df["memory_percent"].std()

df["z_memavl"] = (
    df["memory_available_mb"] - df["memory_available_mb"].mean()
) / df["memory_available_mb"].std()

df["z_disk"] = (
    df["disk_write_mbps"] - df["disk_write_mbps"].mean()
) / df["disk_write_mbps"].std()

# -------------------------
# ROLLING CPU MEAN
# -------------------------

df["rolling_mean_cpu"] = (
    df["cpu_percent"]
    .rolling(window=5, min_periods=1)
    .mean()
)

# -------------------------
# CPU RATE OF CHANGE
# -------------------------

df["cpu_rate_of_change"] = (
    df["cpu_percent"].diff()
)

df["cpu_rate_of_change"] = df["cpu_rate_of_change"].fillna(0)

# -------------------------
# MEMORY DROP RATE
# Positive value means available memory decreased
# -------------------------

df["mem_drop_rate"] = (
    df["memory_available_mb"].shift(1)
    - df["memory_available_mb"]
)

df["mem_drop_rate"] = df["mem_drop_rate"].fillna(0)

# -------------------------
# DISK BURST FLAG
# -------------------------

threshold = df["disk_write_mbps"].quantile(0.95)

df["disk_burst_flag"] = (
    df["disk_write_mbps"] > threshold
).astype(int)

# -------------------------
# PERFORMANCE EVALUATION METRIC (PEM)
# -------------------------

df["pem_score"] = (
    0.30 * abs(df["z_cpu"]) +
    0.30 * abs(df["z_mem"]) +
    0.20 * abs(df["z_memavl"]) +
    0.20 * abs(df["z_disk"])
)

# -------------------------
# ADAPTIVE PEM THRESHOLDS
# -------------------------

pem_warning = df["pem_score"].quantile(0.95)
pem_anomaly = df["pem_score"].quantile(0.99)

print(f"PEM Warning Threshold : {pem_warning:.3f}")
print(f"PEM Anomaly Threshold : {pem_anomaly:.3f}")

# -------------------------
# PEM STATUS
# -------------------------

def classify_pem(score):
    if score >= pem_anomaly:
        return "ANOMALY"
    elif score >= pem_warning:
        return "WARNING"
    else:
        return "NORMAL"

df["pem_status"] = df["pem_score"].apply(classify_pem)

# -------------------------
# MAHALANOBIS DISTANCE
# -------------------------

features = [
    "cpu_percent",
    "memory_percent",
    "memory_available_mb",
    "disk_write_mbps"
]

X = df[features]

# Covariance matrix
cov = np.cov(X.values.T)

# Small regularization to avoid singular matrix
cov += np.eye(cov.shape[0]) * 1e-6

inv_cov = np.linalg.inv(cov)

mean_vector = X.mean().values

# Calculate MD for every row
df["md_score"] = X.apply(
    lambda row: mahalanobis(
        row.values,
        mean_vector,
        inv_cov
    ),
    axis=1
)

# -------------------------
# ADAPTIVE MD THRESHOLDS
# -------------------------

md_warning = df["md_score"].quantile(0.95)
md_anomaly = df["md_score"].quantile(0.99)

print(f"MD Warning Threshold : {md_warning:.3f}")
print(f"MD Anomaly Threshold : {md_anomaly:.3f}")

def classify_md(score):

    if score >= md_anomaly:
        return "ANOMALY"

    elif score >= md_warning:
        return "WARNING"

    else:
        return "NORMAL"

df["md_status"] = df["md_score"].apply(classify_md)

# -------------------------
# FAULT TYPE
# -------------------------

def classify_fault(row):

    cpu = row["cpu_percent"]
    mem = row["memory_percent"]
    disk = row["disk_write_mbps"]

    cpu_high = cpu > 70
    mem_high = mem > 80
    disk_high = disk > 100

    count = sum([cpu_high, mem_high, disk_high])

    if count >= 2:
        return "COMBINED"

    if cpu_high:
        return "CPU"

    if mem_high:
        return "MEMORY"

    if disk_high:
        return "DISK"

    return "NORMAL"


df["fault_type"] = df.apply(classify_fault, axis=1)

# -------------------------
# SEVERITY
# -------------------------

def classify_severity(row):

    if (
        row["pem_status"] == "ANOMALY"
        or row["md_status"] == "ANOMALY"
    ):
        return "HIGH"

    elif (
        row["pem_status"] == "WARNING"
        or row["md_status"] == "WARNING"
    ):
        return "WARNING"

    return "LOW"


df["severity_level"] = df.apply(classify_severity, axis=1)

df.to_csv("final_dataset_v3.csv", index=False)

print("\n✅ Final Dataset Created")

print(df[[
    "fault_type",
    "severity_level"
]].head())

print("\nFault Distribution")
print(df["fault_type"].value_counts())

print("\nSeverity Distribution")
print(df["severity_level"].value_counts())