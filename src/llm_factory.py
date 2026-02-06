import os
from langchain_openai import ChatOpenAI
from langfuse import Langfuse


def create_llm(langfuse: Langfuse):
    """Create LLM instance using OpenRouter"""
    
    return ChatOpenAI(
        model="meta-llama/llama-3.1-8b-instruct",
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.1,
        max_tokens=512,
        default_headers={
            "HTTP-Referer": "https://github.com/incident-commander",
            "X-Title": "Incident Commander"
        }
    )
