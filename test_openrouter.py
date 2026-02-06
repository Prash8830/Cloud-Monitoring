import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

print("Testing OpenRouter Connection...")
token = os.getenv('OPENROUTER_API_KEY')
print(f"OpenRouter Key Set: {'Yes' if token else 'No'}")
print(f"Key prefix: {token[:15] if token else 'N/A'}...")

try:
    llm = ChatOpenAI(
        model="meta-llama/llama-3.1-8b-instruct",
        openai_api_key=token,
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.1,
        max_tokens=50,
        default_headers={
            "HTTP-Referer": "https://github.com/incident-commander",
            "X-Title": "Incident Commander"
        }
    )
    
    response = llm.invoke("Say 'OpenRouter connected' in 5 words")
    print(f"\n✅ Success! Response: {response.content}")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\n⚠️  Check your API key at https://openrouter.ai/keys")
    print("    Key should start with 'sk-or-v1-'")
