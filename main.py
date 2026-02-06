from datetime import datetime
from src.commander import IncidentCommander
from src.models import IncidentInput


def main():
    commander = IncidentCommander()
    
    incident = IncidentInput(
        service="payment-api",
        alert_time=datetime.now(),
        symptoms="High error rate and increased latency on /checkout endpoint",
        logs_path="data/logs.json",
        metrics_path="data/metrics.json",
        deployment_path="data/deployments.json"
    )
    
    print("🚨 Incident Commander Activated")
    print(f"Investigating: {incident.service}")
    print("=" * 80)
    
    report = commander.investigate(incident)
    formatted = commander.format_report(report)
    
    print(formatted)
    
    with open("incident_report.txt", "w") as f:
        f.write(formatted)
    
    print("\n✅ Report saved to incident_report.txt")


if __name__ == "__main__":
    main()
