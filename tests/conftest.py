import pytest
import sys
import os
from pathlib import Path

# Add project root to python path
sys.path.append(str(Path(__file__).parent.parent))

from src.llm_factory import create_llm

from deepeval.models.base_model import DeepEvalBaseLLM

class CustomDeepEvalLLM(DeepEvalBaseLLM):
    def __init__(self, llm):
        self.llm = llm

    def load_model(self):
        return self.llm

    def generate(self, prompt: str) -> str:
        try:
            return self.llm.invoke(prompt).content
        except Exception as e:
            return f"Error generating response: {e}"

    async def a_generate(self, prompt: str) -> str:
        try:
            return (await self.llm.ainvoke(prompt)).content
        except Exception as e:
            return f"Error generating response: {e}"

    def get_model_name(self):
        return "Custom Agent LLM"

@pytest.fixture(scope="session")
def llm():
    return create_llm()

@pytest.fixture(scope="session")
def eval_llm(llm):
    return CustomDeepEvalLLM(llm)

@pytest.fixture
def incident_data():
    return {
        "service": "payment-api",
        "alert_time": "2024-01-15T14:30:00Z",
        "symptoms": "High error rate and increased latency on /checkout endpoint",
        "logs_path": "data/logs.json",
        "metrics_path": "data/metrics.json",
        "deployment_path": "data/deployments.json"
    }

@pytest.fixture
def sample_findings():
    return {
        "logs": ["Database connection timeout", "Connection pool exhausted"],
        "metrics": ["Latency p95 spiked to 3500ms", "CPU usage 92%"],
        "deployments": ["Deploy-789 reduced DB pool size"]
    }
