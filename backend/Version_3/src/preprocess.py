"""
===========================================================
PREPROCESSING MODULE
AI-Based Intelligent Predictive Maintenance System
===========================================================
"""

import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


# ===========================================================
# FEATURES USED FOR TRAINING
# ===========================================================

FEATURES = [
    "cpu_percent",
    "memory_percent",
    "memory_available_mb",
    "disk_write_mbps",
    "z_cpu",
    "z_mem",
    "z_memavl",
    "z_disk",
    "pem_score",
    "md_score",
    "rolling_mean_cpu",
    "cpu_rate_of_change",
    "mem_drop_rate",
    "disk_burst_flag"
]


# ===========================================================
# LOAD DATASET
# ===========================================================

def load_dataset(path):

    print("=" * 60)
    print("Loading dataset...")
    print("=" * 60)

    df = pd.read_csv(path)

    print(f"Rows      : {len(df)}")
    print(f"Columns   : {len(df.columns)}")

    total_missing = df.isnull().sum().sum()
    print(f"Missing Before Cleaning : {total_missing}")

    return df


# ===========================================================
# DATA CLEANING
# ===========================================================

def prepare_data(df):

    X = df[FEATURES].copy()

    y = df["ground_truth"].copy()

    # Convert all feature columns to numeric
    X = X.apply(pd.to_numeric, errors="coerce")

    # Replace missing values using median
    X = X.fillna(X.median(numeric_only=True))

    # Replace infinite values
    X.replace([np.inf, -np.inf], np.nan, inplace=True)
    X.fillna(X.median(numeric_only=True), inplace=True)

    print("\nCleaning Summary")
    print("----------------------------")
    print("Remaining Missing Values :", X.isnull().sum().sum())
    print("Infinite Values          :", np.isinf(X.values).sum())

    return X, y


# ===========================================================
# TRAIN / VALIDATION / TEST SPLIT
# ===========================================================

def split_dataset(X, y):

    X_train, X_temp, y_train, y_temp = train_test_split(
        X,
        y,
        test_size=0.30,
        stratify=y,
        random_state=42
    )

    X_val, X_test, y_val, y_test = train_test_split(
        X_temp,
        y_temp,
        test_size=0.50,
        stratify=y_temp,
        random_state=42
    )

    print("\nDataset Split")
    print("----------------------------")

    print(f"Training Samples   : {len(X_train)}")
    print(f"Validation Samples : {len(X_val)}")
    print(f"Testing Samples    : {len(X_test)}")

    print("\nClass Distribution")

    print("Training")
    print(y_train.value_counts())

    print("\nValidation")
    print(y_val.value_counts())

    print("\nTesting")
    print(y_test.value_counts())

    return (
        X_train,
        X_val,
        X_test,
        y_train,
        y_val,
        y_test
    )


# ===========================================================
# FEATURE SCALING
# ===========================================================

def scale_data(X_train, X_val, X_test):

    print("\nScaling Features...")
    print("----------------------------")

    scaler = StandardScaler()

    X_train_scaled = scaler.fit_transform(X_train)

    X_val_scaled = scaler.transform(X_val)

    X_test_scaled = scaler.transform(X_test)

    print("Scaling Completed Successfully")

    return (
        X_train_scaled,
        X_val_scaled,
        X_test_scaled,
        scaler
    )