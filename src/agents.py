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
        
    def analyze(self, logs_path: str, incident: dict) -> List[str]:
        logs_data = self._load_data(logs_path)
        
        prompt = f"""Follow this workflow:
1. Infer intent: From symptoms '{incident.get('symptoms')}', determine failure type (latency→blocking, error-rate→crashes, memory→leaks)
2. Scope: Filter logs by service '{incident.get('service')}' and severity
3. Filter: Apply intent-driven search for patterns, keywords, errors
4. Reason: Convert log patterns into failure class (DB timeout, thread exhaustion, API failure)
5. Explain: Provide clear evidence

Logs data:
{json.dumps(logs_data, indent=2)}

Return JSON array of findings with evidence."""
        
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
        
    def analyze(self, metrics_path: str, incident: dict) -> List[str]:
        metrics_data = self._load_data(metrics_path)
        
        prompt = f"""Follow this workflow:
1. Window: Look at metrics before, during, after the alert
2. Select metrics: Pull only relevant metrics (latency, CPU, memory, RPS)
3. Analyze shapes: Detect patterns - sudden vs gradual, spike vs saturation
4. Correlate: Compare metrics to identify system behavior (blocking, overload, degradation)
5. Explain: Summarize how the system behaved with evidence

Metrics data:
{json.dumps(metrics_data, indent=2)}

Return JSON array of findings explaining system behavior."""
        
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
        
    def analyze(self, deployment_path: str, incident_time: str, incident: dict) -> List[str]:
        deployment_data = self._load_data(deployment_path)
        
        prompt = f"""Follow this workflow:
1. Normalize: Convert CI/CD events to canonical types (code, config, feature flag, infra)
2. Filter by time: Keep only changes close to incident at {incident_time}
3. Filter by impact: Remove changes that cannot cause this incident type
4. Rank: Score changes by risk and relevance
5. Explain: Output most likely change(s) with reasoning and confidence

Deployment data:
{json.dumps(deployment_data, indent=2)}

Return JSON array of findings with ranked risky changes."""
        
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
