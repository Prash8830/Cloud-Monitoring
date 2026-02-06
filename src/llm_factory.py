import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from langfuse import Langfuse


def create_llm(langfuse: Langfuse = None):
    """Create LLM instance based on provider in .env
    
    Supports:
    - gemini (default): Google's Gemini models
    - anthropic: Anthropic's Claude models
    """
    
    provider = os.getenv("LLM_PROVIDER", "gemini").lower()
    
    if provider == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set in environment")
        
        return ChatAnthropic(
            model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
            anthropic_api_key=api_key,
            temperature=0.1,
            max_tokens=4096
        )
    else:  # default to gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set in environment")
        
        # Use gemini-1.5-flash for better performance and JSON output
        model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        
        return ChatGoogleGenerativeAI(
            model=model,
            google_api_key=api_key,
            temperature=0.1,
            max_tokens=4096,
            convert_system_message_to_human=True  # Better compatibility
        )
