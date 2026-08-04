import csv
import json
import logging
import os
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path

import psutil
from dotenv import load_dotenv

from app.database import SessionLocal
from app.models import Metric, Prediction, AnomalyAlert


load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


# ==========================
# PATH CONFIGURATION
# ==========================

BACKEND_DIR = Path(__file__).resolve().parents[1]

VERSION3_DIR = BACKEND_DIR / "Version_3"

DATA_DIR = VERSION3_DIR / "data"

LIVE_DATA_CSV = DATA_DIR / "live_data.csv"


# ==========================
# CONFIGURATION
# ==========================

COLLECTOR_INTERVAL_SECONDS = int(
    os.getenv(
        "COLLECTOR_INTERVAL_SECONDS",
        "5"
    )
)

SYSTEM_ID = os.getenv(
    "SYSTEM_ID",
    "SYSTEM-01"
)


previous_disk_write = None
previous_time = None


# ==========================
# CSV STORAGE
# ==========================

def _append_live_metric(metric_row: dict):

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    fields = [
    "timestamp",
    "cpu_percent",
    "memory_percent",
    "memory_available_mb",
    "disk_write_mbps",
    "process_count"
]

    file_exists = (
        LIVE_DATA_CSV.exists()
        and LIVE_DATA_CSV.stat().st_size > 0
    )

    with LIVE_DATA_CSV.open(
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fields
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow(metric_row)



# ==========================
# FEATURE PIPELINE
# ==========================

def _trigger_feature_engineering():

    try:

        from Version_3.src.live_monitor import feature_engineering

        feature_engineering.run_feature_engineering()


    except Exception:

        logging.exception(
            "Feature engineering failed"
        )



# ==========================
# PREDICTION PIPELINE
# ==========================

def _run_prediction_and_alert():

    try:

        from Version_3.src.live_monitor.predict import predict_latest

        result = predict_latest()


    except Exception:

        logging.exception(
            "Prediction failed"
        )

        return



    db = SessionLocal()

    try:

        prediction = Prediction(

            system_id=SYSTEM_ID,

            risk_score=float(
                result.get(
                    "risk_score",
                    0
                )
            ),

            risk_level=result.get(
                "risk_level",
                "NORMAL"
            ),

            confidence=float(
                result.get(
                    "confidence",
                    0
                )
            ),

            votes=int(
                result.get(
                    "votes",
                    0
                )
            ),

            fault_type=result.get(
                "fault_type",
                "NONE"
            ),

            severity_level=result.get(
                "severity_level",
                "INFO"
            ),

            pem_status=result.get(
                "pem_status",
                "NORMAL"
            ),

            md_status=result.get(
                "md_status",
                "NORMAL"
            ),

            models_json=json.dumps(
                result.get(
                    "models",
                    {}
                )
            ),

            probabilities_json=json.dumps(
                result.get(
                    "probabilities",
                    {}
                )
            )
        )


        db.add(prediction)

        db.commit()



        risk_level = prediction.risk_level


        if risk_level in [
            "HIGH",
            "CRITICAL"
        ]:

            alert = AnomalyAlert(

                system_id=SYSTEM_ID,

                alert_type=prediction.fault_type,

                severity=prediction.severity_level,

                fault_type=prediction.fault_type
            )


            db.add(alert)

            db.commit()



    finally:

        db.close()



# ==========================
# DATA COLLECTION
# ==========================

def _collect_once():

    global previous_disk_write
    global previous_time


    cpu = psutil.cpu_percent()

    memory = psutil.virtual_memory()

    disk = psutil.disk_io_counters()

    process_count = len(
        psutil.pids()
    )


    current_time = time.time()

    disk_speed = 0.0



    if (
        disk
        and previous_disk_write
        and previous_time
    ):

        delta_bytes = (
            disk.write_bytes
            -
            previous_disk_write
        )

        delta_time = (
            current_time
            -
            previous_time
        )


        if delta_time > 0:

            disk_speed = (
                delta_bytes
                /
                (1024*1024)
                /
                delta_time
            )


    if disk:

        previous_disk_write = (
            disk.write_bytes
        )


    previous_time = current_time



    metric_row = {

        "timestamp":
        datetime.utcnow()
        .strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        "cpu_percent": cpu,

        "memory_percent":
        memory.percent,

        "memory_available_mb":
        round(
            memory.available/(1024*1024),
            2
        ),

        "disk_write_mbps":
        round(
            disk_speed,
            2
        ),

        "process_count":
        process_count
    }



    db = SessionLocal()

    try:

        metric = Metric(
            system_id=SYSTEM_ID,
            **{
                k:v
                for k,v in metric_row.items()
                if k!="timestamp"
            }
        )

        db.add(metric)

        db.commit()


    finally:

        db.close()



    _append_live_metric(
        metric_row
    )


    logging.info(
        "Metrics collected: CPU %.2f%% Memory %.2f%%",
        cpu,
        memory.percent
    )



    _trigger_feature_engineering()

    _run_prediction_and_alert()



# ==========================
# THREAD START
# ==========================

def run_collector_loop():

    logging.info(
        "Collector started"
    )


    while True:

        start=time.time()


        try:

            _collect_once()


        except Exception:

            logging.exception(
                "Collector cycle failed"
            )


        elapsed=time.time()-start


        sleep_time=max(
            0,
            COLLECTOR_INTERVAL_SECONDS-elapsed
        )


        time.sleep(
            sleep_time
        )



def start_collector():

    thread = threading.Thread(

        target=run_collector_loop,

        daemon=True

    )

    thread.start()