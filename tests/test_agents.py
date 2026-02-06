from deepeval import assert_test
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import GEval, AnswerRelevancyMetric
from src.agents import LogsAgent, TelemetryAgent, DeploymentAgent, ReasoningAgent

def test_logs_agent_correctness(llm, eval_llm, incident_data):
    """Evaluate if LogsAgent correctly identifies errors."""
    agent = LogsAgent(llm)
    findings = agent.analyze(incident_data["logs_path"], incident_data)
    
    test_case = LLMTestCase(
        input=f"Analyze logs for {incident_data['service']} with symptoms: {incident_data['symptoms']}",
        actual_output=str(findings),
        expected_output="Identify database connection timeouts, pool exhaustion, and memory errors"
    )
    
    correctness_metric = GEval(
        name="Log Analysis Correctness",
        criteria="Determine if the log findings accurately reflect database connection issues, timeouts, and memory errors based on the expected output.",
        evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
        threshold=0.7,
        model=eval_llm
    )
    
    assert_test(test_case, [correctness_metric])

def test_telemetry_agent_relevancy(llm, eval_llm, incident_data):
    """Evaluate if TelemetryAgent extracts relevant metrics."""
    agent = TelemetryAgent(llm)
    findings = agent.analyze(incident_data["metrics_path"], incident_data)
    
    test_case = LLMTestCase(
        input=f"Analyze metrics for {incident_data['service']}",
        actual_output=str(findings),
        expected_output="Identify CPU spikes, memory saturation, and latency increases"
    )
    
    relevancy_metric = GEval(
        name="Metric Relevancy",
        criteria="Check if the findings include specific quantitative data like '92% CPU' or '3500ms latency' rather than vague statements.",
        evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT],
        threshold=0.7,
        model=eval_llm
    )
    
    assert_test(test_case, [relevancy_metric])

def test_deployment_agent_risk_assessment(llm, eval_llm, incident_data):
    """Evaluate if DeploymentAgent correctly assesses risk."""
    agent = DeploymentAgent(llm)
    # Use string timestamp as expected by the agent
    findings = agent.analyze(incident_data["deployment_path"], incident_data["alert_time"], incident_data)
    
    test_case = LLMTestCase(
        input=f"Analyze deployments before {incident_data['alert_time']}",
        actual_output=str(findings),
        expected_output="Identify deploy-789 as HIGH RISK due to connection pool reduction"
    )
    
    risk_metric = GEval(
        name="Risk Assessment",
        criteria="Ensure the agent correctly identifies the high-risk deployment (deploy-789) that changed connection pool settings.",
        evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
        threshold=0.7,
        model=eval_llm
    )
    
    assert_test(test_case, [risk_metric])

def test_reasoning_agent_logic(llm, eval_llm, sample_findings):
    """Evaluate if ReasoningAgent draws logical conclusions."""
    agent = ReasoningAgent(llm)
    result = agent.correlate(sample_findings["logs"], sample_findings["metrics"], sample_findings["deployments"])
    
    test_case = LLMTestCase(
        input=f"Correlate evidence: Logs={sample_findings['logs']}, Metrics={sample_findings['metrics']}, Deployments={sample_findings['deployments']}",
        actual_output=str(result),
        expected_output="Root cause: Deployment reduced connection pool → Traffic spike → Connection exhaustion"
    )
    
    logic_metric = GEval(
        name="Logical Reasoning",
        criteria="Evaluate if the root cause explanation logically connects the deployment change to the observed errors and metric spikes.",
        evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
        threshold=0.7,
        model=eval_llm
    )
    
    # Also check answer relevancy
    relevancy_metric = AnswerRelevancyMetric(threshold=0.7, model=eval_llm)
    
    assert_test(test_case, [logic_metric, relevancy_metric])
