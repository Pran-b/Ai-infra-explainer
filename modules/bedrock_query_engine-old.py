import boto3
import json
from botocore.exceptions import ClientError
import streamlit as st


def query_bedrock_model(query, text_documents, model_id, aws_access_key=None, aws_secret_key=None, aws_region=None, use_cli_creds=False):
    """Query AWS Bedrock model with the provided documents and query"""
    try:
        # Create Bedrock Runtime client
        if use_cli_creds:
            bedrock_runtime = boto3.client('bedrock-runtime', region_name=aws_region or 'us-east-1')
        else:
            bedrock_runtime = boto3.client(
                'bedrock-runtime',
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=aws_region
            )
        
        # Prepare the context from documents
        context = "\n\n".join(text_documents[:5])  # Limit to first 5 documents to avoid token limits
        
        # Prepare the prompt based on model type
        if "anthropic.claude" in model_id:
            prompt = f"""Human: You are an AWS infrastructure expert. Based on the following AWS infrastructure data, please answer the user's question.

AWS Infrastructure Data:
{context}

User Question: {query}

Please provide a detailed and helpful response about the AWS infrastructure.
Assistant:"""
        else:
            prompt = f"""### Instruction:
You are an AWS infrastructure expert. Based on the following AWS infrastructure data, please answer the user's question.

### AWS Infrastructure Data:
{context}

### User Question:
{query}

### Response:"""

        # Query the Bedrock model
        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            body=json.dumps({"prompt": prompt}),
            contentType="application/json",
            accept="application/json"
        )
        
        # Parse and return the model response
        response_body = json.loads(response['body'].read())
        answer = response_body.get('completions', [{}])[0].get('text', '').strip()
        return answer
    
    except ClientError as e:
        st.error(f"ClientError: {e}")
        return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None
