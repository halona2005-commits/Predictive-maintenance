"""
===========================================================
LIVE PREDICTION SERVICE
===========================================================

Real-time ensemble prediction engine.

Reads:
    data/live_features.csv

Uses:
    Random Forest
    XGBoost
    Isolation Forest
    One-Class SVM
    Compressed Isolation Forest
    LSTM Autoencoder

Returns:
    Risk score
    Confidence
    Model votes
    Fault type
    Severity
    Probabilities

===========================================================
"""

from pathlib import Path
BASE_DIR = Path(__file__).resolve().parents[2]
DATA = BASE_DIR / "data" / "live_features.csv"
import sys
import logging

import joblib
import pandas as pd
import numpy as np


# ---------------------------------------------------------
# PATH SETUP
# ---------------------------------------------------------

SRC_PATH = Path(__file__).resolve().parents[2]

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


from Version_3.src.algorithms.lstm_autoencoder import LSTMAutoencoder
from Version_3.src.live_monitor.risk_engine import calculate_risk


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


# ---------------------------------------------------------
# DIRECTORIES
# ---------------------------------------------------------

BACKEND_DIR = Path(__file__).resolve().parents[3]

VERSION3_DIR = BACKEND_DIR / "Version_3"

DATA_DIR = VERSION3_DIR / "data"

MODEL_DIR = VERSION3_DIR / "models"


DATA_FILE = DATA_DIR / "live_features.csv"


# ---------------------------------------------------------
# MODEL PATHS
# ---------------------------------------------------------

RF_MODEL = MODEL_DIR / "random_forest.pkl"

XGB_MODEL = MODEL_DIR / "xgboost.pkl"

ISO_MODEL = MODEL_DIR / "isolation_forest.pkl"

OCSVM_MODEL = MODEL_DIR / "oneclass_svm.pkl"

COMPRESSED_MODEL = MODEL_DIR / "compressed_if.pkl"

SCALER = MODEL_DIR / "scaler.pkl"



# ---------------------------------------------------------
# FEATURES USED BY ALL MODELS
# ---------------------------------------------------------

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



# ---------------------------------------------------------
# MODEL CACHE
# ---------------------------------------------------------

_models = None



def load_models():

    global _models


    if _models is not None:
        return _models


    logging.info("Loading models...")


    _models = {


        "rf":
            joblib.load(RF_MODEL),


        "xgb":
            joblib.load(XGB_MODEL),


        "iso":
            joblib.load(ISO_MODEL),


        "ocsvm":
            joblib.load(OCSVM_MODEL),


        "compressed":
            joblib.load(COMPRESSED_MODEL),


        "scaler":
            joblib.load(SCALER)

    }



    lstm = LSTMAutoencoder()

    lstm.load()


    _models["lstm"] = lstm



    logging.info("All models loaded")


    return _models



# ---------------------------------------------------------
# DATA CLEANING
# ---------------------------------------------------------


def clean_input(df):

    df = df.apply(
        pd.to_numeric,
        errors="coerce"
    )


    df = df.replace(
        [
            np.inf,
            -np.inf
        ],
        0
    )


    df = df.fillna(0)


    return df
# ===========================================================
# PREDICTION
# ===========================================================

def predict_latest():

    models = load_models()

    if not DATA.exists():
        raise FileNotFoundError(
            "live_features.csv not found"
        )

    df = pd.read_csv(DATA)

    if len(df) == 0:
        raise ValueError(
            "live_features.csv is empty"
        )


    latest = df.iloc[[-1]]


    # -------------------------------------------------------
    # Prepare Features
    # -------------------------------------------------------

    X_raw = latest[FEATURES].copy()


    X_raw = X_raw.apply(
        pd.to_numeric,
        errors="coerce"
    )


    X_raw = X_raw.replace(
        [float("inf"), float("-inf")],
        0
    )


    X_raw = X_raw.fillna(0)



    X = models["scaler"].transform(
        X_raw
    )



    # =======================================================
    # RANDOM FOREST
    # =======================================================

    rf = models["rf"]


    rf_pred = int(
        rf.predict(X)[0]
    )


    rf_prob = float(
        rf.predict_proba(X)[0][1]
    )



    # =======================================================
    # XGBOOST
    # =======================================================

    xgb = models["xgb"]


    xgb_pred = int(
        xgb.predict(X)[0]
    )


    xgb_prob = float(
        xgb.predict_proba(X)[0][1]
    )



    # =======================================================
    # ISOLATION FOREST
    # =======================================================

    iso = models["iso"]


    iso_score = float(
        iso["model"].decision_function(X)[0]
    )


    iso_pred = int(
        iso_score < iso["threshold"]
    )



    # =======================================================
    # ONE CLASS SVM
    # =======================================================

    ocsvm = models["ocsvm"]


    svm_score = float(
        ocsvm["model"].decision_function(X)[0]
    )


    svm_pred = int(
        svm_score < ocsvm["threshold"]
    )



    # =======================================================
    # COMPRESSED ISOLATION FOREST
    # =======================================================

    compressed = models["compressed"]


    compressed_pred = int(
        compressed.predict(X)[0]
    )


    compressed_prob = float(
        compressed.predict_proba(X)[0][1]
    )



    # =======================================================
    # LSTM AUTOENCODER
    # =======================================================

    lstm_pred = 0


    sequence = df[FEATURES].tail(5).copy()


    sequence = sequence.apply(
        pd.to_numeric,
        errors="coerce"
    )


    sequence = sequence.replace(
        [float("inf"), float("-inf")],
        0
    )


    sequence = sequence.fillna(0)



    if len(sequence) == 5:


        X_seq = models["scaler"].transform(
            sequence
        )


        X_seq = X_seq.reshape(
            1,
            5,
            len(FEATURES)
        )


        lstm_pred = int(
            models["lstm"].predict(X_seq)[0]
        )



    # =======================================================
    # RISK ENGINE
    # =======================================================

    risk = calculate_risk(

        rf_pred,

        xgb_pred,

        iso_pred,

        svm_pred,

        compressed_pred,

        lstm_pred,


        latest["pem_score"].iloc[0],

        latest["pem_status"].iloc[0],


        latest["md_score"].iloc[0],

        latest["md_status"].iloc[0]

    )



    logging.info(
        "Prediction completed | Risk=%s",
        risk["risk"]
    )



    return {


        "timestamp":
        latest["timestamp"].iloc[0],


        "risk_score":
        risk["score"],


        "risk_level":
        risk["risk"],


        "confidence":
        risk["confidence"],


        "votes":
        risk["votes"],


        "fault_type":
        latest["fault_type"].iloc[0],


        "severity_level":
        latest["severity_level"].iloc[0],


        "pem_status":
        latest["pem_status"].iloc[0],


        "md_status":
        latest["md_status"].iloc[0],


        "models":
        risk["models"],



        "probabilities":{

            "Random Forest":
            round(rf_prob,3),


            "XGBoost":
            round(xgb_prob,3),


            "Compressed IF":
            round(compressed_prob,3)

        }

    }