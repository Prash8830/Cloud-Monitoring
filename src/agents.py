import json
import re
from pathlib import Path
from typing import List, Union
from langchain_core.messages import SystemMessage, HumanMessage


def extract_json(text: str) -> Union[dict, list, None]:
    """Extract JSON from LLM response that may contain markdown code blocks."""
    if not text:
        return None
    
    # Try to parse directly first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # Try to extract from markdown code blocks
    patterns = [
        r'```json\s*([\s\S]*?)\s*```',  # ```json ... ```
        r'```\s*([\s\S]*?)\s*```',       # ``` ... ```
        r'\[[\s\S]*\]',                   # Array pattern
        r'\{[\s\S]*\}',                   # Object pattern
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            try:
                json_str = match.group(1) if '```' in pattern else match.group(0)
                return json.loads(json_str.strip())
            except (json.JSONDecodeError, IndexError):
                continue
    
    return None


class OrchestratorAgent:
    def __init__(self, llm):
        self.llm = llm
        
    def create_plan(self, incident: dict) -> List[str]:
        prompt = f"""Create a focused investigation plan for this incident:
Service: {incident.get('service')}
Symptoms: {incident.get('symptoms')}
Alert Time: {incident.get('alert_time')}

Return a JSON array of 4-5 specific investigation steps.
Example: ["Check error logs for payment-api between 14:00-15:00", "Analyze latency metrics", ...]"""
        
        try:
            response = self.llm.invoke([
                SystemMessage(content="You are an incident response expert. Return ONLY a valid JSON array, no markdown."),
                HumanMessage(content=prompt)
            ])
            
            result = extract_json(response.content)
            if isinstance(result, list) and len(result) > 0:
                return result
        except Exception as e:
            print(f"[OrchestratorAgent] Error: {e}")
        
        return ["Analyze error logs for patterns", "Check system metrics for anomalies", 
                "Review recent deployments", "Correlate timeline of events", "Identify root cause"]


class LogsAgent:
    def __init__(self, llm):
        self.llm = llm
        
    def analyze(self, logs_path: str, incident: dict) -> List[str]:
        logs_data = self._load_data(logs_path)
        
        if isinstance(logs_data, dict) and logs_data.get("error"):
            return [f"Error loading logs: {logs_data.get('error')}"]
        
        prompt = f"""Analyze these logs for the incident investigation:

SERVICE: {incident.get('service')}
SYMPTOMS: {incident.get('symptoms')}

LOGS DATA:
{json.dumps(logs_data, indent=2)}

Analyze and find:
1. Error patterns and their frequency
2. Cascading failures across services
3. Resource exhaustion indicators
4. Timeline of error progression

Return a JSON array of detailed findings. Each finding should be a descriptive string.
Example output: ["Database connection timeout at 14:23:45 - connection pool exhausted (5 occurrences)", "Cascading failure: auth-service failed due to payment-api unavailability at 14:24:30"]"""
        
        try:
            response = self.llm.invoke([
                SystemMessage(content="You are an expert log analyst. Return ONLY a valid JSON array of findings, no markdown."),
                HumanMessage(content=prompt)
            ])
            
            result = extract_json(response.content)
            if isinstance(result, list) and len(result) > 0:
                return result
        except Exception as e:
            print(f"[LogsAgent] Error: {e}")
        
        # Fallback: generate basic findings from the data
        findings = []
        if isinstance(logs_data, list):
            error_count = sum(1 for log in logs_data if log.get('level') in ['ERROR', 'CRITICAL'])
            warn_count = sum(1 for log in logs_data if log.get('level') == 'WARN')
            findings.append(f"Analyzed {len(logs_data)} log entries: {error_count} errors, {warn_count} warnings")
            
            # Extract unique error messages
            errors = [log.get('message', 'Unknown error') for log in logs_data if log.get('level') in ['ERROR', 'CRITICAL']]
            for error in errors[:5]:
                findings.append(f"Error: {error}")
        
        return findings if findings else ["No significant log patterns detected"]
    
    def _load_data(self, path: str) -> Union[dict, list]:
        if not path:
            return {"error": "No logs path provided"}
        
        file_path = Path(path)
        if not file_path.exists():
            return {"error": f"Logs file not found: {path}"}
        
        try:
            with open(file_path) as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON in logs file: {e}"}


class TelemetryAgent:
    def __init__(self, llm):
        self.llm = llm
        
    def analyze(self, metrics_path: str, incident: dict) -> List[str]:
        metrics_data = self._load_data(metrics_path)
        
        if isinstance(metrics_data, dict) and metrics_data.get("error"):
            return [f"Error loading metrics: {metrics_data.get('error')}"]
        
        prompt = f"""Analyze these system metrics for the incident:

SERVICE: {incident.get('service')}
SYMPTOMS: {incident.get('symptoms')}

METRICS DATA:
{json.dumps(metrics_data, indent=2)}

Analyze and find:
1. Resource saturation (CPU, memory, connections)
2. Latency spikes and their timing
3. Error rate changes (before vs during incident)
4. Request rate anomalies
5. Correlation between different metrics

Return a JSON array of detailed findings with specific numbers and timestamps.
Example: ["Latency p95 increased 29x from 120ms to 3500ms during incident", "Database connection pool saturated: 10/10 active with 127 waiting requests"]"""
        
        try:
            response = self.llm.invoke([
                SystemMessage(content="You are a metrics analysis expert. Return ONLY a valid JSON array of findings, no markdown."),
                HumanMessage(content=prompt)
            ])
            
            result = extract_json(response.content)
            if isinstance(result, list) and len(result) > 0:
                return result
        except Exception as e:
            print(f"[TelemetryAgent] Error: {e}")
        
        # Fallback: extract key metrics from data
        findings = []
        if isinstance(metrics_data, dict):
            metrics = metrics_data.get('metrics', {})
            
            if 'error_rate' in metrics:
                er = metrics['error_rate']
                findings.append(f"Error rate increased from {er.get('before_incident', 0)}% to {er.get('during_incident', 0)}%")
            
            if 'latency_p95' in metrics:
                lat = metrics['latency_p95']
                findings.append(f"P95 latency: {lat.get('before_incident', 0)}ms → {lat.get('during_incident', 0)}ms")
            
            if 'database_connections' in metrics:
                db = metrics['database_connections']
                findings.append(f"Database connections: {db.get('active', 0)}/{db.get('pool_size', 0)} active, {db.get('waiting', 0)} waiting")
        
        return findings if findings else ["Metrics data analyzed"]
    
    def _load_data(self, path: str) -> Union[dict, list]:
        if not path:
            return {"error": "No metrics path provided"}
        
        file_path = Path(path)
        if not file_path.exists():
            return {"error": f"Metrics file not found: {path}"}
        
        try:
            with open(file_path) as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON in metrics file: {e}"}


class DeploymentAgent:
    def __init__(self, llm):
        self.llm = llm
        
    def analyze(self, deployment_path: str, incident_time: str, incident: dict) -> List[str]:
        deployment_data = self._load_data(deployment_path)
        
        if isinstance(deployment_data, dict) and deployment_data.get("error"):
            return [f"Error loading deployments: {deployment_data.get('error')}"]
        
        prompt = f"""Analyze deployments to find the root cause:

INCIDENT TIME: {incident_time}
SERVICE: {incident.get('service')}
SYMPTOMS: {incident.get('symptoms')}

DEPLOYMENT DATA:
{json.dumps(deployment_data, indent=2)}

For each deployment, analyze:
1. Time proximity to incident (deployments just before incident are suspicious)
2. Type of change (config changes are high risk)
3. Specific changes that could cause the symptoms
4. Risk level (HIGH/MEDIUM/LOW)

Return a JSON array of findings with risk assessment.
Example: ["HIGH RISK: deploy-789 at 14:15 reduced DB pool from 20 to 10, just 8 minutes before incident", "MEDIUM RISK: New payment provider integration could increase database load"]"""
        
        try:
            response = self.llm.invoke([
                SystemMessage(content="You are a deployment analysis expert. Return ONLY a valid JSON array of findings, no markdown."),
                HumanMessage(content=prompt)
            ])
            
            result = extract_json(response.content)
            if isinstance(result, list) and len(result) > 0:
                return result
        except Exception as e:
            print(f"[DeploymentAgent] Error: {e}")
        
        # Fallback: summarize deployments
        findings = []
        if isinstance(deployment_data, list):
            for deploy in deployment_data:
                changes = deploy.get('changes', [])
                findings.append(f"{deploy.get('deployment_id')}: {deploy.get('service')} v{deploy.get('version')} at {deploy.get('deployed_at')} - {', '.join(changes[:2])}")
        
        return findings if findings else ["Deployment data analyzed"]
    
    def _load_data(self, path: str) -> Union[dict, list]:
        if not path:
            return {"error": "No deployment path provided"}
        
        file_path = Path(path)
        if not file_path.exists():
            return {"error": f"Deployment file not found: {path}"}
        
        try:
            with open(file_path) as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON in deployment file: {e}"}


class ReasoningAgent:
    def __init__(self, llm):
        self.llm = llm
        
    def correlate(self, logs: List[str], telemetry: List[str], deployment: List[str]) -> dict:
        prompt = f"""You are an expert SRE performing root cause analysis. Correlate ALL the evidence:

=== LOGS EVIDENCE ===
{json.dumps(logs, indent=2)}

=== TELEMETRY EVIDENCE ===
{json.dumps(telemetry, indent=2)}

=== DEPLOYMENT EVIDENCE ===
{json.dumps(deployment, indent=2)}

Create a causal chain:
1. What deployment change triggered the issue?
2. How did it affect system resources (metrics)?
3. What errors resulted (logs)?

Return ONLY this JSON structure:
{{
  "root_cause": "Clear technical explanation connecting deployment → metrics → logs",
  "confidence": 85,
  "supporting_evidence": ["Evidence 1", "Evidence 2", "Evidence 3"],
  "causal_chain": "Deployment X → Resource exhaustion → Error cascade"
}}"""
        
        try:
            response = self.llm.invoke([
                SystemMessage(content="You are an expert SRE. Return ONLY valid JSON, no markdown or explanation."),
                HumanMessage(content=prompt)
            ])
            
            result = extract_json(response.content)
            if isinstance(result, dict) and result.get("root_cause"):
                # Ensure all required fields exist
                result.setdefault("confidence", 70)
                result.setdefault("supporting_evidence", [])
                result.setdefault("causal_chain", "")
                return result
        except Exception as e:
            print(f"[ReasoningAgent] Error: {e}")
        
        # Fallback: create basic correlation
        return {
            "root_cause": "Analysis indicates potential configuration or resource exhaustion issue based on error patterns in logs and metric anomalies",
            "confidence": 50,
            "supporting_evidence": logs[:2] + telemetry[:2] + deployment[:2],
            "causal_chain": "Deployment change → Resource constraints → Error cascade"
        }


class ReportAgent:
    def __init__(self, llm):
        self.llm = llm
        
    def generate(self, state: dict) -> dict:
        prompt = f"""Generate mitigation actions for this incident:

ROOT CAUSE: {state.get('root_cause_hypothesis', 'Unknown')}
CONFIDENCE: {state.get('confidence', 0)}%
EVIDENCE: {json.dumps(state.get('supporting_evidence', []), indent=2)}

Generate 3-5 prioritized mitigation actions:
1. IMMEDIATE: Stop the bleeding (rollback, scale up, circuit breaker)
2. SHORT-TERM: Fix the root cause (config fix, resource adjustment)
3. LONG-TERM: Prevent recurrence (monitoring, testing, safeguards)

Return ONLY this JSON structure:
{{
  "actions": [
    {{"rank": 1, "action": "Specific action", "risk_level": "low", "expected_impact": "What it fixes", "timeline": "immediate"}}
  ],
  "risk_notes": ["Risk 1", "Risk 2"],
  "next_steps": ["Step 1", "Step 2"]
}}"""
        
        try:
            response = self.llm.invoke([
                SystemMessage(content="You are an expert SRE. Return ONLY valid JSON, no markdown."),
                HumanMessage(content=prompt)
            ])
            
            result = extract_json(response.content)
            if isinstance(result, dict) and result.get("actions"):
                result.setdefault("risk_notes", [])
                result.setdefault("next_steps", [])
                return result
        except Exception as e:
            print(f"[ReportAgent] Error: {e}")
        
        # Fallback: generate basic recommendations
        return {
            "actions": [
                {"rank": 1, "action": "Rollback recent deployment if possible", "risk_level": "medium", "expected_impact": "Restore previous stable state", "timeline": "immediate"},
                {"rank": 2, "action": "Scale up affected resources", "risk_level": "low", "expected_impact": "Increase capacity", "timeline": "immediate"},
                {"rank": 3, "action": "Review and adjust configuration", "risk_level": "low", "expected_impact": "Fix root cause", "timeline": "hours"}
            ],
            "risk_notes": ["Rollback may affect in-flight transactions", "Monitor closely after changes"],
            "next_steps": ["Continue monitoring error rates", "Schedule post-incident review"]
        }
