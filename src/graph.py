from typing import TypedDict, Annotated
from operator import add
from langgraph.graph import StateGraph, END
from langfuse import Langfuse
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
    recommended_actions: list[dict]
    final_report: dict


def create_incident_graph(langfuse: Langfuse):
    llm = create_llm(langfuse)
    
    orchestrator = OrchestratorAgent(llm)
    logs_agent = LogsAgent(llm)
    telemetry_agent = TelemetryAgent(llm)
    deployment_agent = DeploymentAgent(llm)
    reasoning_agent = ReasoningAgent(llm)
    report_agent = ReportAgent(llm)
    
    def orchestrate_node(state: GraphState) -> GraphState:
        state["investigation_plan"] = orchestrator.create_plan(state["incident"])
        return state
    
    def logs_node(state: GraphState) -> GraphState:
        logs_path = state["incident"].get("logs_path")
        state["logs_findings"] = logs_agent.analyze(logs_path, state["incident"]) if logs_path else []
        return state
    
    def telemetry_node(state: GraphState) -> GraphState:
        metrics_path = state["incident"].get("metrics_path")
        state["telemetry_findings"] = telemetry_agent.analyze(metrics_path, state["incident"]) if metrics_path else []
        return state
    
    def deployment_node(state: GraphState) -> GraphState:
        deployment_path = state["incident"].get("deployment_path")
        incident_time = state["incident"].get("alert_time")
        state["deployment_findings"] = deployment_agent.analyze(deployment_path, str(incident_time), state["incident"]) if deployment_path else []
        return state
    
    def reasoning_node(state: GraphState) -> GraphState:
        result = reasoning_agent.correlate(
            state["logs_findings"],
            state["telemetry_findings"],
            state["deployment_findings"]
        )
        state["root_cause_hypothesis"] = result.get("root_cause", "Unknown")
        state["confidence"] = result.get("confidence", 0)
        return state
    
    def report_node(state: GraphState) -> GraphState:
        report_data = report_agent.generate(state)
        
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
                confidence=state["confidence"],
                supporting_evidence=state["logs_findings"][:3]
            ),
            recommended_actions=[
                MitigationAction(**action) for action in report_data.get("actions", [])
            ],
            risk_notes=report_data.get("risk_notes", []),
            next_steps=report_data.get("next_steps", [])
        )
        
        state["final_report"] = final_report.model_dump()
        return state
    
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
