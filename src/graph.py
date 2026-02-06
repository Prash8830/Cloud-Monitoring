from typing import TypedDict
from langgraph.graph import StateGraph, END
from src.llm_factory import create_llm
from src.agents import OrchestratorAgent, LogsAgent, TelemetryAgent, DeploymentAgent, ReasoningAgent, ReportAgent
from src.models import IncidentReport, Evidence, RootCause, MitigationAction


class GraphState(TypedDict):
    incident: dict
    investigation_plan: list[str]
    logs_findings: list[str]
    telemetry_findings: list[str]
    deployment_findings: list[str]
    root_cause_hypothesis: str
    confidence: int
    supporting_evidence: list[str]
    causal_chain: str
    recommended_actions: list[dict]
    final_report: dict


def create_incident_graph():
    """Create the incident investigation workflow graph."""
    
    llm = create_llm()
    
    orchestrator = OrchestratorAgent(llm)
    logs_agent = LogsAgent(llm)
    telemetry_agent = TelemetryAgent(llm)
    deployment_agent = DeploymentAgent(llm)
    reasoning_agent = ReasoningAgent(llm)
    report_agent = ReportAgent(llm)
    
    def orchestrate_node(state: GraphState) -> GraphState:
        print("📋 Creating investigation plan...")
        state["investigation_plan"] = orchestrator.create_plan(state["incident"])
        print(f"   ✓ Plan created with {len(state['investigation_plan'])} steps")
        return state
    
    def logs_node(state: GraphState) -> GraphState:
        print("📜 Analyzing logs...")
        logs_path = state["incident"].get("logs_path")
        if logs_path:
            state["logs_findings"] = logs_agent.analyze(logs_path, state["incident"])
            print(f"   ✓ Found {len(state['logs_findings'])} log findings")
        else:
            state["logs_findings"] = ["No logs path provided"]
            print("   ⚠ No logs path provided")
        return state
    
    def telemetry_node(state: GraphState) -> GraphState:
        print("📊 Analyzing metrics...")
        metrics_path = state["incident"].get("metrics_path")
        if metrics_path:
            state["telemetry_findings"] = telemetry_agent.analyze(metrics_path, state["incident"])
            print(f"   ✓ Found {len(state['telemetry_findings'])} metric findings")
        else:
            state["telemetry_findings"] = ["No metrics path provided"]
            print("   ⚠ No metrics path provided")
        return state
    
    def deployment_node(state: GraphState) -> GraphState:
        print("🚀 Analyzing deployments...")
        deployment_path = state["incident"].get("deployment_path")
        incident_time = state["incident"].get("alert_time")
        if deployment_path:
            state["deployment_findings"] = deployment_agent.analyze(
                deployment_path, str(incident_time), state["incident"]
            )
            print(f"   ✓ Found {len(state['deployment_findings'])} deployment findings")
        else:
            state["deployment_findings"] = ["No deployment path provided"]
            print("   ⚠ No deployment path provided")
        return state
    
    def reasoning_node(state: GraphState) -> GraphState:
        print("🔍 Correlating evidence and determining root cause...")
        result = reasoning_agent.correlate(
            state["logs_findings"],
            state["telemetry_findings"],
            state["deployment_findings"]
        )
        state["root_cause_hypothesis"] = result.get("root_cause", "Unknown")
        state["confidence"] = result.get("confidence", 0)
        state["supporting_evidence"] = result.get("supporting_evidence", [])
        state["causal_chain"] = result.get("causal_chain", "")
        print(f"   ✓ Root cause identified with {state['confidence']}% confidence")
        return state
    
    def report_node(state: GraphState) -> GraphState:
        print("📝 Generating incident report...")
        report_data = report_agent.generate(state)
        
        # Safely create mitigation actions
        actions = []
        for action in report_data.get("actions", []):
            try:
                # Ensure all required fields are present
                action.setdefault("rank", len(actions) + 1)
                action.setdefault("action", "Review and monitor")
                action.setdefault("risk_level", "low")
                action.setdefault("expected_impact", "TBD")
                actions.append(MitigationAction(**action))
            except Exception as e:
                print(f"   ⚠ Error creating action: {e}")
        
        final_report = IncidentReport(
            incident_summary={
                "service": state["incident"]["service"],
                "impact": state["incident"]["symptoms"],
                "start_time": str(state["incident"]["alert_time"]),
                "symptoms": state["incident"]["symptoms"]
            },
            investigation_plan=state["investigation_plan"],
            logs_evidence=Evidence(source="logs", findings=state["logs_findings"]),
            telemetry_evidence=Evidence(source="telemetry", findings=state["telemetry_findings"]),
            deployment_evidence=Evidence(source="deployment", findings=state["deployment_findings"]),
            root_cause=RootCause(
                explanation=state["root_cause_hypothesis"],
                confidence=min(100, max(0, state["confidence"])),  # Clamp to 0-100
                supporting_evidence=state.get("supporting_evidence", [])
            ),
            recommended_actions=actions,
            risk_notes=report_data.get("risk_notes", []),
            next_steps=report_data.get("next_steps", [])
        )
        
        state["final_report"] = final_report.model_dump()
        print(f"   ✓ Report generated with {len(actions)} recommendations")
        return state
    
    # Build workflow graph
    workflow = StateGraph(GraphState)
    
    workflow.add_node("orchestrate", orchestrate_node)
    workflow.add_node("logs", logs_node)
    workflow.add_node("telemetry", telemetry_node)
    workflow.add_node("deployment", deployment_node)
    workflow.add_node("reasoning", reasoning_node)
    workflow.add_node("report", report_node)
    
    workflow.set_entry_point("orchestrate")
    workflow.add_edge("orchestrate", "logs")
    workflow.add_edge("logs", "telemetry")
    workflow.add_edge("telemetry", "deployment")
    workflow.add_edge("deployment", "reasoning")
    workflow.add_edge("reasoning", "report")
    workflow.add_edge("report", END)
    
    return workflow.compile()
