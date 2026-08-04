from pathlib import Path

import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
VERSION3_DIR = ROOT / "Version-3"
INPUT_FILE = VERSION3_DIR / "data" / "live_data.csv"
OUTPUT_FILE = VERSION3_DIR / "models" / "baseline_statistics.pkl"


def run_calibration() -> dict:
    df = pd.read_csv(INPUT_FILE)

    if len(df) < 30:
        raise ValueError(
            f"Collect at least 30 samples before calibration. Currently have {len(df)}."
        )

    cpu_mean = df["cpu_percent"].mean()
    mem_mean = df["memory_percent"].mean()
    mem_avl_mean = df["memory_available_mb"].mean()
    disk_mean = df["disk_write_mbps"].mean()

    cpu_std = df["cpu_percent"].std()
    mem_std = df["memory_percent"].std()
    mem_avl_std = df["memory_available_mb"].std()
    disk_std = df["disk_write_mbps"].std()

    cov_matrix = df[
        ["cpu_percent", "memory_percent", "memory_available_mb", "disk_write_mbps"]
    ].cov()
    cov_inv = np.linalg.inv(cov_matrix)

    baseline = {
        "cpu_mean": cpu_mean,
        "cpu_std": cpu_std,
        "mem_mean": mem_mean,
        "mem_std": mem_std,
        "mem_avl_mean": mem_avl_mean,
        "mem_avl_std": mem_avl_std,
        "disk_mean": disk_mean,
        "disk_std": disk_std,
        "covariance": cov_matrix,
        "inverse_covariance": cov_inv,
    }

    joblib.dump(baseline, OUTPUT_FILE)

    return {
        "samples_used": len(df),
        "cpu_mean": float(cpu_mean),
        "cpu_std": float(cpu_std),
        "mem_mean": float(mem_mean),
        "mem_std": float(mem_std),
    }