"""
===========================================================
SYSTEM CALIBRATION
Version 3
===========================================================
"""

import joblib
import numpy as np
import pandas as pd

INPUT_FILE = "../../data/live_data.csv"
OUTPUT_FILE = "../../models/baseline_statistics.pkl"

print("=" * 60)
print("SYSTEM CALIBRATION")
print("=" * 60)

# -------------------------------------------------------
# Read live data
# -------------------------------------------------------

df = pd.read_csv(INPUT_FILE)
# -------------------------------------------------------
# Temporary Z Scores for Calibration
# -------------------------------------------------------

cpu_mean = df["cpu_percent"].mean()
cpu_std = df["cpu_percent"].std()

mem_mean = df["memory_percent"].mean()
mem_std = df["memory_percent"].std()

mem_avl_mean = df["memory_available_mb"].mean()
mem_avl_std = df["memory_available_mb"].std()

disk_mean = df["disk_write_mbps"].mean()
disk_std = df["disk_write_mbps"].std()

df["z_cpu"] = (
    df["cpu_percent"] - cpu_mean
) / cpu_std

df["z_mem"] = (
    df["memory_percent"] - mem_mean
) / mem_std

df["z_memavl"] = (
    mem_avl_mean -
    df["memory_available_mb"]
) / mem_avl_std

df["z_disk"] = (
    df["disk_write_mbps"] -
    disk_mean
) / disk_std

# -------------------------------------------------------
# Calibration PEM
# -------------------------------------------------------

df["pem_score"] = (

    0.40 * df["z_cpu"]

    +

    0.35 * np.maximum(
        df["z_mem"],
        df["z_memavl"]
    )

    +

    0.25 * df["z_disk"]

)

print(f"Samples Collected : {len(df)}")

# -------------------------------------------------------
# Minimum samples check
# -------------------------------------------------------

if len(df) < 30:
    raise ValueError(
        "Collect at least 30 samples before calibration."
    )

# -------------------------------------------------------
# Mean
# -------------------------------------------------------

cpu_mean = df["cpu_percent"].mean()
mem_mean = df["memory_percent"].mean()
mem_avl_mean = df["memory_available_mb"].mean()
disk_mean = df["disk_write_mbps"].mean()

# -------------------------------------------------------
# Standard Deviation
# -------------------------------------------------------

cpu_std = df["cpu_percent"].std()
mem_std = df["memory_percent"].std()
mem_avl_std = df["memory_available_mb"].std()
disk_std = df["disk_write_mbps"].std()

# -------------------------------------------------------
# Percentiles (NEW)
# -------------------------------------------------------

cpu_p95 = df["cpu_percent"].quantile(0.95)
cpu_p99 = df["cpu_percent"].quantile(0.99)

mem_p95 = df["memory_percent"].quantile(0.95)
mem_p99 = df["memory_percent"].quantile(0.99)

disk_p95 = df["disk_write_mbps"].quantile(0.95)
disk_p99 = df["disk_write_mbps"].quantile(0.99)

pem_mean = df["pem_score"].mean()

pem_std = df["pem_score"].std()

pem_p95 = df["pem_score"].quantile(0.95)

pem_p99 = df["pem_score"].quantile(0.99)

# -------------------------------------------------------
# Covariance Matrix
# -------------------------------------------------------

cov_matrix = df[
    [
        "cpu_percent",
        "memory_percent",
        "memory_available_mb",
        "disk_write_mbps"
    ]
].cov()

# -------------------------------------------------------
# Inverse Covariance Matrix
# -------------------------------------------------------

cov_inv = np.linalg.inv(cov_matrix)

# -------------------------------------------------------
# Mahalanobis Scores During Calibration
# -------------------------------------------------------

features = df[
    [
        "cpu_percent",
        "memory_percent",
        "memory_available_mb",
        "disk_write_mbps"
    ]
].values

mean_vector = np.array([
    cpu_mean,
    mem_mean,
    mem_avl_mean,
    disk_mean
])

md_scores = []

for row in features:

    diff = row - mean_vector

    md = np.sqrt(
        diff.T @ cov_inv @ diff
    )

    md_scores.append(md)

df["md_score"] = md_scores

md_mean = df["md_score"].mean()

md_std = df["md_score"].std()

md_p95 = df["md_score"].quantile(0.95)

md_p99 = df["md_score"].quantile(0.99)

# -------------------------------------------------------
# Save
# -------------------------------------------------------

baseline = {

    "cpu_mean": cpu_mean,
    "cpu_std": cpu_std,
    "cpu_p95": cpu_p95,
    "cpu_p99": cpu_p99,

    "mem_mean": mem_mean,
    "mem_std": mem_std,
    "mem_p95": mem_p95,
    "mem_p99": mem_p99,

    "mem_avl_mean": mem_avl_mean,
    "mem_avl_std": mem_avl_std,

    "disk_mean": disk_mean,
    "disk_std": disk_std,
    "disk_p95": disk_p95,
    "disk_p99": disk_p99,

    "pem_mean": pem_mean,

    "pem_std": pem_std,

    "pem_p95": pem_p95,

    "pem_p99": pem_p99,

    "md_mean": md_mean,
    "md_std": md_std,
    "md_p95": md_p95,
    "md_p99": md_p99,

    "covariance": cov_matrix,
    "inverse_covariance": cov_inv
}

joblib.dump(
    baseline,
    OUTPUT_FILE
)

print("\nBaseline Statistics Saved")

print("\nCPU Mean :", cpu_mean)
print("CPU Std  :", cpu_std)
print("CPU P95  :", cpu_p95)
print("CPU P99  :", cpu_p99)

print("\nMemory Mean :", mem_mean)
print("Memory Std  :", mem_std)
print("Memory P95  :", mem_p95)
print("Memory P99  :", mem_p99)

print("\nDisk Mean :", disk_mean)
print("Disk Std  :", disk_std)
print("Disk P95  :", disk_p95)
print("Disk P99  :", disk_p99)

print("\nPEM Mean :", pem_mean)
print("PEM Std  :", pem_std)
print("PEM P95  :", pem_p95)
print("PEM P99  :", pem_p99)

print("\nMD Mean :", md_mean)
print("MD Std  :", md_std)
print("MD P95  :", md_p95)
print("MD P99  :", md_p99)

print("\nCalibration Complete.")