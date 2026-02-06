import os
import boto3
from dotenv import load_dotenv
from langchain_aws import ChatBedrock

load_dotenv()

print("Testing AWS Bedrock Connection...")
bearer_token = os.getenv('AWS_BEARER_TOKEN_BEDROCK')
print(f"Bearer Token Set: {'Yes' if bearer_token else 'No'}")
print(f"Token prefix: {bearer_token[:20] if bearer_token else 'N/A'}...")

try:
    print("\nAttempt 1: Using bearer token as session token...")
    bedrock_client = boto3.client(
        service_name='bedrock-runtime',
        region_name='us-east-1',
        aws_access_key_id='BEARER_TOKEN',
        aws_secret_access_key='BEARER_TOKEN',
        aws_session_token=bearer_token
    )
    
    llm = ChatBedrock(
        model="global.anthropic.claude-sonnet-4-5-20250929-v1:0",
        client=bedrock_client,
        model_kwargs={"temperature": 0}
    )
    
    response = llm.invoke("Say 'Bedrock connected successfully' in 5 words or less")
    print(f"\n✅ Success! Response: {response.content}")
    
except Exception as e:
    print(f"❌ Failed: {str(e)[:200]}")
    
    try:
        print("\nAttempt 2: Using default AWS credentials...")
        bedrock_client = boto3.client(
            service_name='bedrock-runtime',
            region_name='us-east-1'
        )
        
        llm = ChatBedrock(
            model="global.anthropic.claude-sonnet-4-5-20250929-v1:0",
            client=bedrock_client,
            model_kwargs={"temperature": 0}
        )
        
        response = llm.invoke("Say 'Bedrock connected successfully' in 5 words or less")
        print(f"\n✅ Success! Response: {response.content}")
    except Exception as e2:
        print(f"❌ Failed: {str(e2)[:200]}")
        print("\n⚠️  ISSUE: Your IAM user has an explicit DENY policy for bedrock:InvokeModel")
        print("    Contact your AWS admin to grant bedrock:InvokeModel permission.")
