import json
from pathlib import Path
from typing import List
from langchain_core.messages import SystemMessage, HumanMessage


class OrchestratorAgent:
    def __init__(self, llm):
        self.llm = llm
        
    def create_plan(self, incident: dict) -> List[str]:
        prompt = f"""Create investigation plan for: {json.dumps(incident, default=str)}
Return JSON array of 3-5 steps."""
        
        response = self.llm.invoke([
            SystemMessage(content="Return only JSON array."),
            HumanMessage(content=prompt)
        ])
        
        try:
            return json.loads(response.content)
        except:
            return ["Analyze logs", "Check metrics", "Review deployments", "Correlate findings"]


class LogsAgent:
    def __init__(self, llm):
        self.llm = llm
        
    def analyze(self, logs_path: str) -> List[str]:
        logs_data = self._load_data(logs_path)
        
        prompt = f"""Analyze logs for errors, exceptions, patterns:
{json.dumps(logs_data, indent=2)}
Return JSON array of findings."""
        
        response = self.llm.invoke([
            SystemMessage(content="Return only JSON array."),
            HumanMessage(content=prompt)
        ])
        
        try:
            return json.loads(response.content)
        except:
            return [f"Analyzed {len(logs_data) if isinstance(logs_data, list) else 0} log entries"]
    
    def _load_data(self, path: str) -> dict:
        if not path or not Path(path).exists():
            return {"error": "No logs available"}
        with open(path) as f:
            return json.load(f)


class TelemetryAgent:
    def __init__(self, llm):
        self.llm = llm
        
    def analyze(self, metrics_path: str) -> List[str]:
        metrics_data = self._load_data(metrics_path)
        
        prompt = f"""Analyze metrics for anomalies:
{json.dumps(metrics_data, indent=2)}
Return JSON array of findings."""
        
        response = self.llm.invoke([
            SystemMessage(content="Return only JSON array."),
            HumanMessage(content=prompt)
        ])
        
        try:
            return json.loads(response.content)
        except:
            return ["Analyzed metrics data"]
    
    def _load_data(self, path: str) -> dict:
        if not path or not Path(path).exists():
            return {"error": "No metrics available"}
        with open(path) as f:
            return json.load(f)


class DeploymentAgent:
    def __init__(self, llm):
        self.llm = llm
        
    def analyze(self, deployment_path: str, incident_time: str) -> List[str]:
        deployment_data = self._load_data(deployment_path)
        
        prompt = f"""Analyze deployments before incident at {incident_time}:
{json.dumps(deployment_data, indent=2)}
Return JSON array of findings."""
        
        response = self.llm.invoke([
            SystemMessage(content="Return only JSON array."),
            HumanMessage(content=prompt)
        ])
        
        try:
            return json.loads(response.content)
        except:
            return ["Analyzed deployment data"]
    
    def _load_data(self, path: str) -> dict:
        if not path or not Path(path).exists():
            return {"error": "No deployment data"}
        with open(path) as f:
            return json.load(f)


class ReasoningAgent:
    def __init__(self, llm):
        self.llm = llm
        
    def correlate(self, logs: List[str], telemetry: List[str], deployment: List[str]) -> dict:
        prompt = f"""Correlate evidence and determine root cause:
Logs: {json.dumps(logs)}
Telemetry: {json.dumps(telemetry)}
Deployment: {json.dumps(deployment)}

Return JSON: {{"root_cause": "...", "confidence": 0-100, "supporting_evidence": []}}"""
        
        response = self.llm.invoke([
            SystemMessage(content="Return only JSON."),
            HumanMessage(content=prompt)
        ])
        
        try:
            return json.loads(response.content)
        except:
            return {"root_cause": "Unable to determine", "confidence": 30, "supporting_evidence": []}


class ReportAgent:
    def __init__(self, llm):
        self.llm = llm
        
    def generate(self, state: dict) -> dict:
        prompt = f"""Generate mitigation actions for:
Root Cause: {state.get('root_cause_hypothesis')}
Confidence: {state.get('confidence')}%

Return JSON: {{"actions": [{{"rank": 1, "action": "...", "risk_level": "low", "expected_impact": "..."}}], "risk_notes": [], "next_steps": []}}"""
        
        response = self.llm.invoke([
            SystemMessage(content="Return only JSON."),
            HumanMessage(content=prompt)
        ])
        
        try:
            return json.loads(response.content)
        except:
            return {
                "actions": [{"rank": 1, "action": "Monitor and collect more data", "risk_level": "low", "expected_impact": "Gather information"}],
                "risk_notes": ["Insufficient data"],
                "next_steps": ["Continue monitoring"]
            }
