from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class IncidentInput(BaseModel):
    service: str
    alert_time: datetime
    symptoms: str
    logs_path: Optional[str] = None
    metrics_path: Optional[str] = None
    deployment_path: Optional[str] = None


class Evidence(BaseModel):
    source: str
    findings: List[str]
    timestamp_range: Optional[str] = None


class RootCause(BaseModel):
    explanation: str
    confidence: int = Field(ge=0, le=100)
    supporting_evidence: List[str]


class MitigationAction(BaseModel):
    rank: int
    action: str
    risk_level: str
    expected_impact: str


class IncidentReport(BaseModel):
    incident_summary: dict
    investigation_plan: List[str]
    logs_evidence: Evidence
    telemetry_evidence: Evidence
    deployment_evidence: Evidence
    root_cause: RootCause
    recommended_actions: List[MitigationAction]
    risk_notes: List[str]
    next_steps: List[str]
