"""
===========================================================
LIVE FEATURE ENGINEERING SERVICE
===========================================================

Converts collected system metrics into ML features.

Input:
    Version_3/data/live_data.csv

Output:
    Version_3/data/live_features.csv

Called by:
    collector_loop.py

Function:
    run_feature_engineering()

===========================================================
"""


from pathlib import Path
import logging

import joblib
import pandas as pd
import numpy as np



logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)



# ===========================================================
# PATH CONFIGURATION
# ===========================================================


BACKEND_DIR = Path(__file__).resolve().parents[3]

VERSION3_DIR = BACKEND_DIR / "Version_3"

DATA_DIR = VERSION3_DIR / "data"

MODEL_DIR = VERSION3_DIR / "models"



LIVE_DATA = DATA_DIR / "live_data.csv"

BASELINE = MODEL_DIR / "baseline_statistics.pkl"

OUTPUT = DATA_DIR / "live_features.csv"





# ===========================================================
# MAIN FEATURE ENGINEERING FUNCTION
# ===========================================================


def run_feature_engineering():

    logging.info(
        "Starting feature engineering"
    )


    if not LIVE_DATA.exists():

        logging.warning(
            "live_data.csv not found"
        )

        return None



    if not BASELINE.exists():

        logging.error(
            "baseline_statistics.pkl not found"
        )

        return None



    # -------------------------------------------------------
    # Load Data
    # -------------------------------------------------------

    df = pd.read_csv(
        LIVE_DATA
    )


    baseline = joblib.load(
        BASELINE
    )



    # -------------------------------------------------------
    # Z Scores
    # -------------------------------------------------------


    df["z_cpu"] = (

        df["cpu_percent"]
        -
        baseline["cpu_mean"]

    ) / baseline["cpu_std"]



    df["z_mem"] = (

        df["memory_percent"]
        -
        baseline["mem_mean"]

    ) / baseline["mem_std"]



    # lower memory availability means worse condition

    df["z_memavl"] = (

        baseline["mem_avl_mean"]
        -
        df["memory_available_mb"]

    ) / baseline["mem_avl_std"]



    df["z_disk"] = (

        df["disk_write_mbps"]
        -
        baseline["disk_mean"]

    ) / baseline["disk_std"]



    logging.info(
        "Z scores generated"
    )



    # -------------------------------------------------------
    # Rolling CPU Mean
    # -------------------------------------------------------


    df["rolling_mean_cpu"] = (

        df["cpu_percent"]
        .rolling(
            window=5,
            min_periods=1
        )
        .mean()

    )



    # -------------------------------------------------------
    # CPU Rate Change
    # -------------------------------------------------------


    df["cpu_rate_of_change"] = (

        df["cpu_percent"]
        .diff()
        .fillna(0)

    )



    # -------------------------------------------------------
    # Memory Drop Rate
    # -------------------------------------------------------


    df["mem_drop_rate"] = (

        df["memory_available_mb"]
        .diff()
        .fillna(0)
        *
        -1

    )



    # -------------------------------------------------------
    # Disk Burst Detection
    # -------------------------------------------------------


    threshold = (

        baseline["disk_mean"]
        +
        (
            2 *
            baseline["disk_std"]
        )

    )


    df["disk_burst_flag"] = (

        df["disk_write_mbps"]
        >
        threshold

    ).astype(int)



    # -------------------------------------------------------
    # Performance Evaluation Metric
    # -------------------------------------------------------


    df["pem_score"] = (

        0.40 *
        df["z_cpu"]

        +

        0.35 *
        np.maximum(
            df["z_mem"],
            df["z_memavl"]
        )

        +

        0.25 *
        df["z_disk"]

    )



    logging.info(
        "PEM score generated"
    )



    # -------------------------------------------------------
    # PEM Status
    # -------------------------------------------------------


    pem_warning = baseline["pem_p95"]

    pem_anomaly = baseline["pem_p99"]



    df["pem_status"] = np.select(

        [

            df["pem_score"] >= pem_anomaly,

            df["pem_score"] >= pem_warning

        ],

        [

            "ANOMALY",

            "WARNING"

        ],

        default="NORMAL"

    )



    # -------------------------------------------------------
    # Mahalanobis Distance
    # -------------------------------------------------------


    features = df[

        [

            "cpu_percent",

            "memory_percent",

            "memory_available_mb",

            "disk_write_mbps"

        ]

    ].values



    mean_vector = np.array(

        [

            baseline["cpu_mean"],

            baseline["mem_mean"],

            baseline["mem_avl_mean"],

            baseline["disk_mean"]

        ]

    )



    cov_inv = baseline["inverse_covariance"]



    md_scores = []



    for row in features:


        diff = row - mean_vector


        md = np.sqrt(

            diff.T
            @
            cov_inv
            @
            diff

        )


        md_scores.append(md)



    df["md_score"] = md_scores



    logging.info(
        "Mahalanobis distance generated"
    )



    # -------------------------------------------------------
    # MD Status
    # -------------------------------------------------------


    md_warning = baseline["md_p95"]

    md_anomaly = baseline["md_p99"]



    df["md_status"] = np.select(

        [

            df["md_score"] >= md_anomaly,

            df["md_score"] >= md_warning

        ],

        [

            "ANOMALY",

            "WARNING"

        ],

        default="NORMAL"

    )



    # -------------------------------------------------------
    # Final Decision
    # -------------------------------------------------------


    df["is_anomaly"] = (

        (

            df["pem_status"]
            ==
            "ANOMALY"

        )

        &

        (

            df["md_status"]
            ==
            "ANOMALY"

        )

    ).astype(int)




    # -------------------------------------------------------
    # Severity
    # -------------------------------------------------------


    severity = []



    for _, row in df.iterrows():


        if row["is_anomaly"] == 1:

            severity.append(
                "CRITICAL"
            )


        elif (

            row["pem_status"] == "WARNING"

            or

            row["md_status"] == "WARNING"

        ):

            severity.append(
                "WARNING"
            )


        else:

            severity.append(
                "NORMAL"
            )



    df["severity_level"] = severity




    # -------------------------------------------------------
    # Fault Type
    # -------------------------------------------------------


    faults = []



    for _, row in df.iterrows():


        values = {


            "CPU":
            row["z_cpu"],


            "MEMORY":
            max(
                row["z_mem"],
                row["z_memavl"]
            ),


            "DISK":
            row["z_disk"]

        }


        faults.append(

            max(
                values,
                key=values.get
            )

        )



    df["fault_type"] = faults



    # -------------------------------------------------------
    # Save Features
    # -------------------------------------------------------


    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )



    df.to_csv(

        OUTPUT,

        index=False

    )



    logging.info(
        "Live features saved: %s",
        OUTPUT
    )



    return OUTPUT