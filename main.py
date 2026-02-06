from datetime import datetime
from pathlib import Path
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
    
    # Create reports directory if it doesn't exist
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    # Save report with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = reports_dir / f"incident_report_{timestamp}.txt"
    
    with open(report_file, "w") as f:
        f.write(formatted)
    
    print(f"\n✅ Report saved to {report_file}")


if __name__ == "__main__":
    main()
