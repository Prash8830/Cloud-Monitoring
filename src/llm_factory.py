import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langfuse import Langfuse


def create_llm(langfuse: Langfuse):
    """Create LLM instance using Gemini"""
    
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.1,
        max_tokens=512
    )
