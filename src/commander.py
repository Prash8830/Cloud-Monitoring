import os
from dotenv import load_dotenv
from langfuse import Langfuse
from src.graph import create_incident_graph
from src.models import IncidentInput


class IncidentCommander:
    def __init__(self):
        load_dotenv()
        self.langfuse = Langfuse(
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
        )
        self.graph = create_incident_graph(self.langfuse)
    
    def investigate(self, incident: IncidentInput) -> dict:
        initial_state = {
            "incident": incident.model_dump(),
            "investigation_plan": [],
            "logs_findings": [],
            "telemetry_findings": [],
            "deployment_findings": [],
            "root_cause_hypothesis": "",
            "confidence": 0,
            "supporting_evidence": [],
            "causal_chain": "",
            "recommended_actions": [],
            "final_report": {}
        }
        
        result = self.graph.invoke(initial_state)
        return result["final_report"]
    
    def format_report(self, report: dict) -> str:
        output = ["=" * 80, "INCIDENT RESPONSE REPORT", "=" * 80]
        
        summary = report["incident_summary"]
        output.append("\n### 1. Incident Summary")
        output.append(f"•  Service: {summary['service']}")
        output.append(f"•  Impact: {summary['impact']}")
        output.append(f"•  Start Time: {summary['start_time']}")
        output.append(f"•  Symptoms: {summary['symptoms']}")
        
        output.append("\n### 2. Investigation Plan")
        for i, step in enumerate(report["investigation_plan"], 1):
            output.append(f"{i}. {step}")
        
        output.append("\n### 3. Findings (Evidence)")
        output.append("\n#### Logs Evidence")
        for finding in report["logs_evidence"]["findings"]:
            output.append(f"  - {finding}")
        
        output.append("\n#### Telemetry Evidence")
        for finding in report["telemetry_evidence"]["findings"]:
            output.append(f"  - {finding}")
        
        output.append("\n#### Deployment Evidence")
        for finding in report["deployment_evidence"]["findings"]:
            output.append(f"  - {finding}")
        
        output.append("\n### 4. Root Cause Hypothesis")
        output.append(f"•  Explanation: {report['root_cause']['explanation']}")
        output.append(f"•  Confidence: {report['root_cause']['confidence']}%")
        
        output.append("\n### 5. Supporting Evidence")
        for evidence in report['root_cause']['supporting_evidence']:
            output.append(f"  - {evidence}")
        
        output.append("\n### 6. Recommended Actions (Ranked)")
        for action in report["recommended_actions"]:
            output.append(f"{action['rank']}. {action['action']}")
            output.append(f"   Risk: {action['risk_level']} | Impact: {action['expected_impact']}")
        
        output.append("\n### 7. Risk Notes")
        for note in report["risk_notes"]:
            output.append(f"•  {note}")
        
        output.append("\n### 8. Next Steps / Follow-up")
        for step in report["next_steps"]:
            output.append(f"•  {step}")
        
        output.append("\n" + "=" * 80)
        return "\n".join(output)
