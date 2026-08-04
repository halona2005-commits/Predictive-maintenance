from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel


class MetricCreate(BaseModel):
    cpu_percent: float
    memory_percent: float
    memory_available_mb: float
    disk_write_mbps: float
    process_count: int


class MetricOut(BaseModel):
    id: int
    timestamp: datetime
    system_id: str
    cpu_percent: float
    memory_percent: float
    memory_available_mb: float
    disk_write_mbps: float
    process_count: int

    class Config:
        from_attributes = True


class PredictionOut(BaseModel):
    timestamp: str
    risk_score: float
    risk_level: str
    confidence: float
    votes: int
    fault_type: str
    severity_level: str
    pem_status: str
    md_status: str
    models: Dict[str, int]
    probabilities: Dict[str, float]


class AlertOut(BaseModel):
    id: int
    timestamp: datetime
    system_id: str
    alert_type: str
    severity: str
    fault_type: str
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StatusOut(BaseModel):
    risk_level: str
    fault_type: str
    severity_level: str


class HistoryResponse(BaseModel):
    metrics: list[MetricOut]