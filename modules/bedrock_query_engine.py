import json
import boto3
from botocore.exceptions import ClientError
import streamlit as st


def query_bedrock_model(query, text_documents, model_id, aws_access_key=None, aws_secret_key=None, aws_region=None, use_cli_creds=False, debug=False, aws_profile=None):
    """Query AWS Bedrock model with the provided documents and query"""
    try:
        # Create Bedrock Runtime client
        if use_cli_creds:
            if aws_profile and aws_profile != "default":
                session = boto3.Session(profile_name=aws_profile)
                bedrock_runtime = session.client('bedrock-runtime', region_name=aws_region or 'us-east-1')
            else:
                bedrock_runtime = boto3.client('bedrock-runtime', region_name=aws_region or 'us-east-1')
        else:
            bedrock_runtime = boto3.client(
                'bedrock-runtime',
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=aws_region
            )
        
        # Prepare optimized context based on model token limits
        # Be more conservative with token limits to avoid "Input is too long" errors
        max_input_tokens = 8000  # Very conservative limit for input
        context = prepare_optimal_context(text_documents, query, max_input_tokens)
        
        if debug:
            st.info(f"Context length: {len(context)} characters (~{estimate_tokens(context)} tokens)")
            st.info(f"Query length: {len(query)} characters (~{estimate_tokens(query)} tokens)")
            estimated_total = estimate_tokens(context) + estimate_tokens(query) + 500  # 500 for prompt structure
            st.info(f"Estimated total input tokens: {estimated_total}")
            
        # Double-check context length and truncate if necessary
        if estimate_tokens(context) > max_input_tokens - 1000:
            context = truncate_context_aggressively(context, max_input_tokens - 1000)
            if debug:
                st.warning(f"Context was too long, truncated to {len(context)} characters (~{estimate_tokens(context)} tokens)")
        
        # Pre-flight check to prevent "Input is too long" errors
        total_estimated_tokens = estimate_tokens(context) + estimate_tokens(query) + 1000
        if total_estimated_tokens > max_input_tokens:
            st.error(f"🚨 **Input Too Long - Pre-flight Check**")
            st.error(f"Estimated total tokens: {total_estimated_tokens}, limit: {max_input_tokens}")
            st.info("**Suggestions:**")
            st.info("1. Try asking a more specific question")
            st.info("2. Use fewer AWS resources or regions")
            st.info("3. Enable debug mode to see exact token counts")
            
            # Offer to try with an even smaller context
            if len(context) > 1000:
                st.info("💡 **Auto-recovery attempt**: Trying with minimal context...")
                context = create_minimal_context(text_documents, query)
                total_estimated_tokens = estimate_tokens(context) + estimate_tokens(query) + 1000
                if total_estimated_tokens <= max_input_tokens:
                    st.success(f"✅ Reduced context to {estimate_tokens(context)} tokens, proceeding...")
                else:
                    return None
            else:
                return None
        
        # Prepare the prompt based on model type
        if "anthropic.claude" in model_id or "inference-profile" in model_id or model_id.startswith("us."):
            prompt = f"""Human: You are an AWS infrastructure expert analyzing actual AWS infrastructure data. You have been provided with real AWS infrastructure data below.

IMPORTANT: The AWS infrastructure data provided below is real and current. Please analyze this data carefully to answer the user's question.

AWS Infrastructure Data:
{context}

User Question: {query}

Instructions:
1. Look carefully at the AWS infrastructure data provided above
2. If you see EC2 instances in the data, list their details including Instance IDs, states, and types
3. If you see other AWS resources, analyze them as requested
4. If the data contains information relevant to the question, use it to provide a comprehensive answer
5. If you truly cannot find relevant information in the provided data, then explain what data would be needed

Please provide a detailed and helpful response based on the actual AWS infrastructure data provided.
Assistant:"""
            
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2000,  # Reduced to leave more room for input
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
            
        elif "amazon.titan" in model_id:
            prompt = f"""You are an AWS infrastructure expert analyzing actual AWS infrastructure data. You have been provided with real AWS infrastructure data below.

IMPORTANT: The AWS infrastructure data provided below is real and current. Please analyze this data carefully to answer the user's question.

AWS Infrastructure Data:
{context}

User Question: {query}

Instructions:
1. Look carefully at the AWS infrastructure data provided above
2. If you see EC2 instances in the data, list their details including Instance IDs, states, and types
3. If you see other AWS resources, analyze them as requested
4. If the data contains information relevant to the question, use it to provide a comprehensive answer
5. If you truly cannot find relevant information in the provided data, then explain what data would be needed

Please provide a detailed and helpful response based on the actual AWS infrastructure data provided."""
            
            body = json.dumps({
                "inputText": prompt,
                "textGenerationConfig": {
                    "maxTokenCount": 2000,  # Reduced to leave more room for input
                    "temperature": 0.1,
                    "topP": 0.9
                }
            })
            
        elif "ai21.j2" in model_id:
            prompt = f"""You are an AWS infrastructure expert. Based on the following AWS infrastructure data, please answer the user's question.

AWS Infrastructure Data:
{context}

User Question: {query}

Please provide a detailed and helpful response about the AWS infrastructure."""
            
            body = json.dumps({
                "prompt": prompt,
                "maxTokens": 2000,  # Reduced to leave more room for input
                "temperature": 0.1
            })
            
        elif "cohere.command" in model_id:
            prompt = f"""You are an AWS infrastructure expert. Based on the following AWS infrastructure data, please answer the user's question.

AWS Infrastructure Data:
{context}

User Question: {query}

Please provide a detailed and helpful response about the AWS infrastructure."""
            
            body = json.dumps({
                "prompt": prompt,
                "max_tokens": 2000,  # Reduced to leave more room for input
                "temperature": 0.1
            })
            
        else:
            # Generic fallback for unknown models
            prompt = f"""You are an AWS infrastructure expert. Based on the following AWS infrastructure data, please answer the user's question.

AWS Infrastructure Data:
{context}

User Question: {query}

Please provide a detailed and helpful response about the AWS infrastructure."""
            
            body = json.dumps({
                "prompt": prompt,
                "max_tokens": 2000,  # Reduced to leave more room for input
                "temperature": 0.1
            })
        
        # Invoke the model
        response = bedrock_runtime.invoke_model(
            body=body,
            modelId=model_id,
            accept='application/json',
            contentType='application/json'
        )
        
        # Parse the response
        response_body = json.loads(response.get('body').read())
        
        # Debug information
        if debug:
            st.write("**Debug - Model Response:**")
            st.json(response_body)
        
        try:
            if "anthropic.claude" in model_id or "inference-profile" in model_id or model_id.startswith("us."):
                result = response_body['content'][0]['text']
            elif "amazon.titan" in model_id:
                result = response_body['results'][0]['outputText']
            elif "ai21.j2" in model_id:
                result = response_body['completions'][0]['data']['text']
            elif "cohere.command" in model_id:
                result = response_body['generations'][0]['text']
            else:
                # Try to extract text from common response formats
                if 'completion' in response_body:
                    result = response_body['completion']
                elif 'text' in response_body:
                    result = response_body['text']
                elif 'generated_text' in response_body:
                    result = response_body['generated_text']
                else:
                    result = str(response_body)
        except (KeyError, IndexError, TypeError) as e:
            st.error(f"Error parsing response from model '{model_id}': {str(e)}")
            st.error(f"Response structure: {json.dumps(response_body, indent=2)}")
            return None
        
        return result
        
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        error_message = e.response.get('Error', {}).get('Message', str(e))
        
        if error_code == 'AccessDenied':
            st.error(f"Access denied to Bedrock model '{model_id}'. Please check your permissions.")
        elif error_code == 'ValidationException':
            if "Input is too long" in error_message or "exceeds the maximum allowed length" in error_message:
                st.error(f"🚨 **Input Too Long Error**")
                st.error(f"The AWS infrastructure data is too large for the model '{model_id}'.")
                st.info("**Suggestions:**")
                st.info("1. Try enabling 'Debug Mode' in Advanced Options to see token counts")
                st.info("2. Use a more specific question to reduce context needed")
                st.info("3. Consider using a different model with larger context window")
                st.info("4. Try splitting your question into smaller parts")
                if debug:
                    st.error(f"Full error message: {error_message}")
            else:
                st.error(f"Invalid request to Bedrock model '{model_id}': {error_message}")
        elif error_code == 'ResourceNotFoundException':
            st.error(f"Bedrock model '{model_id}' not found. Please check the model ID.")
        else:
            st.error(f"Error querying Bedrock model '{model_id}': {error_message}")
        return None
    except Exception as e:
        st.error(f"Unexpected error during Bedrock query with model '{model_id}': {str(e)}")
        return None

def test_bedrock_connection(model_id, aws_access_key=None, aws_secret_key=None, aws_region=None, use_cli_creds=False, aws_profile=None):
    """Test Bedrock connection with a simple query"""
    try:
        # Create Bedrock Runtime client
        if use_cli_creds:
            if aws_profile and aws_profile != "default":
                session = boto3.Session(profile_name=aws_profile)
                bedrock_runtime = session.client('bedrock-runtime', region_name=aws_region or 'us-east-1')
            else:
                bedrock_runtime = boto3.client('bedrock-runtime', region_name=aws_region or 'us-east-1')
        else:
            bedrock_runtime = boto3.client(
                'bedrock-runtime',
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=aws_region
            )
        
        # Simple test query - use Claude format for most models and inference profiles
        if "anthropic.claude" in model_id or "inference-profile" in model_id or model_id.startswith("us."):
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 20,
                "messages": [{"role": "user", "content": "Hello, just say 'Test successful'"}]
            })
        elif "amazon.titan" in model_id:
            body = json.dumps({
                "inputText": "Hello, just say 'Test successful'",
                "textGenerationConfig": {"maxTokenCount": 20}
            })
        else:
            body = json.dumps({
                "prompt": "Hello, just say 'Test successful'",
                "max_tokens": 20
            })
        
        # Test the model
        response = bedrock_runtime.invoke_model(
            body=body,
            modelId=model_id,
            accept='application/json',
            contentType='application/json'
        )
        
        response_body = json.loads(response.get('body').read())
        return True, response_body
        
    except Exception as e:
        return False, str(e)

def create_minimal_context(text_documents, query):
    """Create an extremely minimal context focusing only on query-relevant information"""
    # Keywords from the query to focus on
    query_keywords = [word.lower() for word in query.split() if len(word) > 3]
    
    minimal_info = []
    
    for doc in text_documents[:3]:  # Only first 3 documents
        lines = doc.split('\n')
        relevant_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Only include lines that contain query keywords
            if any(keyword in line.lower() for keyword in query_keywords):
                relevant_lines.append(line)
                
            # Stop if we have enough relevant lines
            if len(relevant_lines) >= 5:
                break
        
        if relevant_lines:
            minimal_info.extend(relevant_lines[:5])
        
        # Limit total information
        if len(minimal_info) >= 10:
            break
    
    if minimal_info:
        return '\n'.join(minimal_info[:10])
    else:
        # If no keyword matches, return first few lines of each document
        fallback_info = []
        for doc in text_documents[:2]:
            lines = doc.split('\n')[:3]
            fallback_info.extend([line.strip() for line in lines if line.strip()])
        return '\n'.join(fallback_info[:8])

def truncate_context_aggressively(context, max_tokens):
    """Aggressively truncate context to fit within token limits"""
    max_chars = max_tokens * 4  # Convert tokens to characters
    
    if len(context) <= max_chars:
        return context
    
    # Take the first portion and add a clear truncation message
    truncated = context[:max_chars - 200]
    
    # Try to cut at a reasonable point (end of line)
    last_newline = truncated.rfind('\n')
    if last_newline > max_chars * 0.8:  # If we can cut at a line break without losing too much
        truncated = truncated[:last_newline]
    
    return truncated + "\n\n[... AWS infrastructure data truncated due to length limits. Please ask more specific questions for detailed information ...]"

def create_aws_summary(text_documents):
    """Create a concise summary of AWS infrastructure data"""
    summary_parts = []
    
    for doc in text_documents[:5]:  # Process fewer documents for better summarization
        lines = doc.split('\n')
        
        # Extract key information from each document
        key_info = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Focus on the most important information
            if any(keyword in line.lower() for keyword in ['instances', 'security', 'vpc', 'subnet', 'volume', 'bucket', 'function', 'table', 'cluster', 'database']):
                key_info.append(line)
        
        if key_info:
            summary_parts.append('\n'.join(key_info[:3]))  # Top 3 items per service
    
    return '\n\n'.join(summary_parts[:3])  # Top 3 services

def estimate_tokens(text):
    """Rough estimation of token count (1 token ≈ 4 characters for most models)"""
    return len(text) // 4

def prepare_optimal_context(text_documents, query, max_tokens=8000):
    """Prepare context that fits within token limits"""
    # Reserve tokens for query, prompt structure, and response
    reserved_tokens = estimate_tokens(query) + 1500  # Increased buffer for prompt structure
    available_tokens = max_tokens - reserved_tokens
    available_chars = available_tokens * 4  # Convert back to characters
    
    # Try different strategies
    if available_tokens <= 500:  # Need minimum space for context
        return "Error: Query too long for available context"
    
    # Strategy 1: Use summary if we have a lot of documents
    if len(text_documents) > 3:
        summary = create_aws_summary(text_documents)
        if len(summary) <= available_chars:
            return summary
    
    # Strategy 2: Use first few documents
    context = ""
    for i, doc in enumerate(text_documents[:5]):  # Reduced from 10 to 5
        potential_context = context + "\n\n" + doc if context else doc
        if len(potential_context) <= available_chars:
            context = potential_context
        else:
            break
    
    # Strategy 3: Truncate if still too long
    if len(context) > available_chars:
        context = context[:available_chars - 200] + "\n\n[... content truncated due to length limits ...]"
    
    return context if context else "No AWS data available"