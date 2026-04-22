from pathlib import Path
import json
from typing import Dict, List, Union
try:
    from fastmcp import FastMCP
except ImportError:
    # Mock for development if library missing
    class FastMCP:
        def __init__(self, name): self.name = name
        def resource(self, uri): 
            def decorator(func): return func
            return decorator
        def run(self): print("FastMCP not installed")

# Initialize FastMCP server
mcp = FastMCP("cloud-monitoring")
DATA_DIR = Path(__file__).parent.parent / "data"

def _load_json_file(filename: str) -> Union[Dict, List]:
    """Helper to load JSON file safely."""
    path = DATA_DIR / filename
    if not path.exists():
        return {"error": f"File not found: {filename}"}
    try:
        with open(path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON in {filename}: {str(e)}"}
    except Exception as e:
        return {"error": f"Error loading {filename}: {str(e)}"}

@mcp.resource("monitoring://logs")
def get_logs() -> str:
    """Get all system logs."""
    data = _load_json_file("logs.json")
    return json.dumps(data, indent=2)

@mcp.resource("monitoring://metrics")
def get_metrics() -> str:
    """Get system metrics."""
    data = _load_json_file("metrics.json")
    return json.dumps(data, indent=2)

@mcp.resource("monitoring://deployments")
def get_deployments() -> str:
    """Get deployment history."""
    data = _load_json_file("deployments.json")
    return json.dumps(data, indent=2)

if __name__ == "__main__":
    mcp.run()
