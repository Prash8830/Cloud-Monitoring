from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from src.commander import IncidentCommander
from src.models import IncidentInput

app = FastAPI(title="Incident Commander API", description="API for autonomous incident investigation")

commander = IncidentCommander()

class IncidentRequest(BaseModel):
    service: str
    alert_time: str  # ISO format string
    symptoms: str
    logs_path: str = None
    metrics_path: str = None
    deployment_path: str = None

class ParseReportRequest(BaseModel):
    formatted_report: str

@app.post("/investigate")
async def investigate_incident(request: IncidentRequest):
    incident = IncidentInput(
        service=request.service,
        alert_time=datetime.fromisoformat(request.alert_time),
        symptoms=request.symptoms,
        logs_path=request.logs_path,
        metrics_path=request.metrics_path,
        deployment_path=request.deployment_path
    )
    
    report = commander.investigate(incident)
    return report

@app.post("/parse_report")
async def parse_report(request: ParseReportRequest):
    parsed = commander.parse_formatted_report(request.formatted_report)
    return parsed

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
