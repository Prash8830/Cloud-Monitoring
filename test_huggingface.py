import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpoint
import traceback

load_dotenv()

print("Testing Hugging Face Connection...")
token = os.getenv('HUGGINGFACEHUB_API_TOKEN')
print(f"HF Token Set: {'Yes' if token else 'No'}")

try:
    llm = HuggingFaceEndpoint(
        repo_id="mistralai/Mistral-7B-Instruct-v0.2",
        huggingfacehub_api_token=token,
        temperature=0.1,
        max_new_tokens=50
    )
    
    response = llm.invoke("Say 'HuggingFace connected' in 5 words")
    print(f"\n✅ Success! Response: {response}")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    traceback.print_exc()
