import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import get_db, init_db
from app.models import AnomalyAlert, Metric, Prediction
from app.schemas import AlertOut, HistoryResponse, MetricCreate, MetricOut, PredictionOut, StatusOut

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

VERSION3_DIR = BASE_DIR / "Version_3"
SRC_DIR = VERSION3_DIR / "src"

sys.path.append(str(BASE_DIR))
sys.path.append(str(VERSION3_DIR))
sys.path.append(str(SRC_DIR))

app = FastAPI(title="Predictive Maintenance API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SYSTEM_ID = os.getenv("SYSTEM_ID", "SYSTEM-01")


@app.on_event("startup")
def startup_event() -> None:
    init_db()
    from app.collector_loop import start_collector
    start_collector()


@app.post("/metrics", response_model=MetricOut)
def create_metric(payload: MetricCreate, db: Session = Depends(get_db)) -> MetricOut:
    metric = Metric(
        system_id=SYSTEM_ID,
        cpu_percent=payload.cpu_percent,
        memory_percent=payload.memory_percent,
        memory_available_mb=payload.memory_available_mb,
        disk_write_mbps=payload.disk_write_mbps,
        process_count=payload.process_count,
    )
    db.add(metric)
    db.commit()
    db.refresh(metric)
    return metric


@app.get("/predict", response_model=PredictionOut)
def get_prediction(db: Session = Depends(get_db)) -> PredictionOut:
    try:
        from live_monitor.predict import predict_latest
        result = predict_latest()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}") from exc

    if not isinstance(result, dict):
        raise HTTPException(status_code=500, detail="Prediction module returned an invalid result")

    models_clean = {k: int(v) for k, v in result.get("models", {}).items()}
    probabilities_clean = {k: float(v) for k, v in result.get("probabilities", {}).items()}

    prediction = Prediction(
        system_id=SYSTEM_ID,
        risk_score=float(result.get("risk_score", 0.0)),
        risk_level=str(result.get("risk_level", "NORMAL")),
        confidence=float(result.get("confidence", 0.0)),
        votes=int(result.get("votes", 0)),
        fault_type=str(result.get("fault_type", "NONE")),
        severity_level=str(result.get("severity_level", "INFO")),
        pem_status=str(result.get("pem_status", "NORMAL")),
        md_status=str(result.get("md_status", "NORMAL")),
        models_json=json.dumps(models_clean),
        probabilities_json=json.dumps(probabilities_clean),
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    return PredictionOut(
        timestamp=str(result.get("timestamp", "")),
        risk_score=float(result.get("risk_score", 0.0)),
        risk_level=str(result.get("risk_level", "NORMAL")),
        confidence=float(result.get("confidence", 0.0)),
        votes=int(result.get("votes", 0)),
        fault_type=str(result.get("fault_type", "NONE")),
        severity_level=str(result.get("severity_level", "INFO")),
        pem_status=str(result.get("pem_status", "NORMAL")),
        md_status=str(result.get("md_status", "NORMAL")),
        models=models_clean,
        probabilities=probabilities_clean,
    )


@app.get("/alerts", response_model=list[AlertOut])
def get_alerts(db: Session = Depends(get_db)) -> list[AlertOut]:
    return db.query(AnomalyAlert).order_by(AnomalyAlert.id.desc()).limit(20).all()


@app.get("/status", response_model=StatusOut)
def get_status(db: Session = Depends(get_db)) -> StatusOut:
    latest = db.query(Prediction).order_by(Prediction.id.desc()).first()
    if latest is None:
        return StatusOut(risk_level="NORMAL", fault_type="NONE", severity_level="INFO")
    return StatusOut(
        risk_level=latest.risk_level,
        fault_type=latest.fault_type,
        severity_level=latest.severity_level,
    )


@app.get("/history", response_model=HistoryResponse)
def get_history(db: Session = Depends(get_db)) -> HistoryResponse:
    metrics = db.query(Metric).order_by(Metric.id.desc()).limit(100).all()
    metrics = list(reversed(metrics))
    return HistoryResponse(metrics=[MetricOut.model_validate(m, from_attributes=True) for m in metrics])

@app.get("/risk-history")
def get_risk_history(db: Session = Depends(get_db)):
    predictions = (
        db.query(Prediction)
        .order_by(Prediction.id.desc())
        .limit(30)
        .all()
    )

    predictions = list(reversed(predictions))

    return [
        {
            "timestamp": p.timestamp.strftime("%H:%M:%S"),
            "risk_score": p.risk_score,
            "risk_level": p.risk_level,
            "fault_type": p.fault_type
        }
        for p in predictions
    ]


@app.post("/calibrate")
def calibrate() -> dict:
    try:
        from app.calibration_wrapper import run_calibration
        result = run_calibration()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Calibration failed: {exc}") from exc
    return {"status": "calibrated", **result}