import os
import json
import re
from typing import List
from pydantic import BaseModel, ValidationError
from datetime import datetime
import requests
from dotenv import load_dotenv

from llm.gemeni_client import llm




# ---------------------------------------
# Load environment variables
# ---------------------------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")


# ---------------------------------------
# Pydantic Schema
# ---------------------------------------
class MetricPoint(BaseModel):
    timestamp: datetime
    value: float

class MetricsDataset(BaseModel):
    service_name: str
    instance_id: str
    environment: str
    cpu_usage: List[MetricPoint]
    memory_usage: List[MetricPoint]
    latency_p99: List[MetricPoint]
    error_rate: List[MetricPoint]
    request_throughput: List[MetricPoint]
    anomaly_label: str

# ---------------------------------------
# Gemini LLM API call
# ---------------------------------------
def generate_metrics_sample():
    prompt = """
Generate a synthetic AWS metrics dataset in JSON format for one microservice.
Include:
- service_name (random microservice name)
- instance_id (random pod/container id)
- environment (prod, stage, dev)
- cpu_usage, memory_usage, latency_p99, error_rate, request_throughput (5-10 timestamped points)
- anomaly_label: one of CPU_SPIKE, MEM_LEAK, LATENCY_SPIKE, NORMAL
Output ONLY valid JSON, matching the Pydantic schema MetricsDataset.
"""
    headers = {"Authorization": f"Bearer {GEMINI_API_KEY}"}
    payload = {
        "prompt": prompt,
        "temperature": 0.7,
        "maxOutputTokens": 500
    }

    response = requests.post(GEMINI_API_URL, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()

    # Extract text from response
    try:
        if "candidates" in data:
            text_output = data["candidates"][0].get("content", "")
        elif "output_text" in data:
            text_output = data["output_text"]
        else:
            text_output = str(data)

        # Extract JSON using regex in case LLM adds extra text
        match = re.search(r"\{.*\}", text_output, re.DOTALL)
        if not match:
            print("No valid JSON found in Gemini output")
            print(text_output)
            return None

        json_data = json.loads(match.group(0))
        return json_data
    except Exception as e:
        print("Error parsing JSON from Gemini:", e)
        print(text_output)
        return None

# ---------------------------------------
# Ensure data folder exists
# ---------------------------------------
os.makedirs("data", exist_ok=True)
output_file = os.path.join("data", "synthetic_metrics_20.json")

# ---------------------------------------
# Generate 20 samples
# ---------------------------------------
samples = []
for i in range(20):
    print(f"Generating sample {i+1}/20...")
    sample_json = generate_metrics_sample()
    if sample_json:
        try:
            sample = MetricsDataset(**sample_json)
            samples.append(sample.dict())
        except ValidationError as ve:
            print(f"Validation error for sample {i+1}: {ve}")
            # Optionally save raw JSON if validation fails
            samples.append(sample_json)

# ---------------------------------------
# Save to JSON file
# ---------------------------------------
with open(output_file, "w") as f:
    json.dump(samples, f, indent=2)

print(f"✅ 20 synthetic metrics samples saved to {output_file}")
