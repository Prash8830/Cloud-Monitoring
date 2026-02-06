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
        
        output.append("\n### 5. Recommended Actions (Ranked)")
        for action in report["recommended_actions"]:
            output.append(f"{action['rank']}. {action['action']}")
            output.append(f"   Risk: {action['risk_level']} | Impact: {action['expected_impact']}")
        
        output.append("\n### 6. Confidence Score")
        output.append(f"•  Confidence: {report['root_cause']['confidence']}%")
        
        output.append("\n### 7. Risk Notes")
        for note in report["risk_notes"]:
            output.append(f"•  {note}")
        
        output.append("\n### 8. Next Steps / Follow-up")
        for step in report["next_steps"]:
            output.append(f"•  {step}")
        
        output.append("\n" + "=" * 80)
        return "\n".join(output)

    def parse_formatted_report(self, formatted_str: str) -> dict:
        """Parse the formatted report string back into a dictionary structure."""
        lines = formatted_str.split('\n')
        report = {}

        current_section = None
        current_data = []

        for line in lines:
            line = line.strip()
            if line.startswith('### '):
                if current_section:
                    report[current_section] = self._parse_section(current_section, current_data)
                current_section = line[4:].lower().replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_')
                current_data = []
            elif current_section:
                current_data.append(line)

        if current_section:
            report[current_section] = self._parse_section(current_section, current_data)

        return report

    def _parse_section(self, section: str, data: list) -> any:
        """Parse individual sections into appropriate data structures."""
        if section == '1._incident_summary':
            summary = {}
            for line in data:
                if line.startswith('• '):
                    key_value = line[2:].split(': ', 1)
                    if len(key_value) == 2:
                        key = key_value[0].lower().replace(' ', '_')
                        summary[key] = key_value[1]
            return summary
        elif section in ['2._investigation_plan', '7._risk_notes', '8._next_steps']:
            return [line for line in data if line and not line.startswith('=')]
        elif section in ['3._findings_(evidence)', '4._root_cause_hypothesis', '5._recommended_actions_(ranked)', '6._confidence_score']:
            # For simplicity, return the raw text; could be parsed further
            return '\n'.join(data)
        else:
            return '\n'.join(data)
