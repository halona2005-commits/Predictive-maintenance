"""
===========================================================
PROJECT CONFIGURATION
AI-Based Intelligent Predictive Maintenance
===========================================================
"""

# ===========================================================
# GLOBAL SETTINGS
# ===========================================================

RANDOM_STATE = 42

TEST_SIZE = 0.15

VALIDATION_SIZE = 0.15

# ===========================================================
# RANDOM FOREST
# ===========================================================

RF_PARAMS = {

    "n_estimators": 300,

    "max_depth": 20,

    "min_samples_split": 5,

    "min_samples_leaf": 2,

    "class_weight": "balanced",

    "random_state": RANDOM_STATE,

    "n_jobs": -1

}

# ===========================================================
# ISOLATION FOREST
# ===========================================================

IF_PARAMS = {

    "n_estimators": 200,

    "max_samples": "auto",

    "contamination": "auto",

    "bootstrap": False,

    "random_state": RANDOM_STATE,

    "n_jobs": -1

}

# ===========================================================
# COMPRESSED ISOLATION FOREST
# ===========================================================

CIF_PARAMS = {

    "n_estimators": 50,

    "max_samples": 128,

    "contamination": "auto",

    "bootstrap": False,

    "random_state": RANDOM_STATE,

    "n_jobs": -1

}

TOP_N_FEATURES = 6

# ===========================================================
# ONE CLASS SVM
# ===========================================================

OCSVM_PARAMS = {

    "kernel": "rbf",

    "gamma": "scale",

    "nu": 0.05

}

# ===========================================================
# XGBOOST
# ===========================================================

XGB_PARAMS = {

    "n_estimators": 300,

    "max_depth": 6,

    "learning_rate": 0.05,

    "subsample": 0.8,

    "colsample_bytree": 0.8,

    "eval_metric": "logloss",

    "random_state": RANDOM_STATE,

    "n_jobs": -1

}

# ===========================================================
# LSTM
# ===========================================================

LSTM_TIMESTEPS = 10

LSTM_EPOCHS = 40

LSTM_BATCH_SIZE = 32

LSTM_UNITS = 64

# ===========================================================
# SHAP
# ===========================================================

SHAP_SAMPLE_SIZE = 500

# ===========================================================
# FEATURE LIST
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
# PATHS
# ===========================================================

MODEL_PATH = "../models"

RESULT_PATH = "../results"

PLOT_PATH = "../plots"

DATA_PATH = "../data/final_dataset_complete.csv"