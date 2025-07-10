import boto3
import subprocess
import streamlit as st
from botocore.exceptions import ClientError


def get_available_bedrock_models(aws_access_key=None, aws_secret_key=None, aws_region=None, use_cli_creds=False):
    """Fetch available Bedrock models with access granted based on AWS credentials"""
    try:
        # Create Bedrock client with provided credentials or CLI credentials
        if use_cli_creds:
            # Use AWS CLI credentials (default profile or configured profile)
            bedrock_client = boto3.client('bedrock', region_name=aws_region or 'us-east-1')
        else:
            # Use provided access key and secret key
            bedrock_client = boto3.client(
                'bedrock',
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=aws_region
            )
        
        # Get foundation models with access granted
        response = bedrock_client.list_foundation_models(
            byCustomizationType='FINE_TUNING',  # Optional: filter by customization type
            byOutputModality='TEXT',  # Filter for text output models
            byInferenceType='ON_DEMAND'  # Filter for on-demand inference models
        )
        
        models = []
        accessible_models = []
        
        # First, get all models that support text
        for model in response.get('modelSummaries', []):
            model_id = model.get('modelId', '')
            model_name = model.get('modelName', '')
            
            # Filter for text generation models
            if (model.get('inputModalities') and 'TEXT' in model.get('inputModalities', []) and
                model.get('outputModalities') and 'TEXT' in model.get('outputModalities', [])):
                
                # Check if model access is granted by trying to get model details
                try:
                    # Try to get model details to verify access
                    model_details = bedrock_client.get_foundation_model(modelIdentifier=model_id)
                    
                    # If we can get model details, access is granted
                    accessible_models.append({
                        'id': model_id,
                        'name': f"{model_name} ({model_id})",
                        'provider': model.get('providerName', 'Unknown'),
                        'status': 'ACTIVE'
                    })
                    
                except ClientError as e:
                    # If we get an access denied error, skip this model
                    if 'AccessDenied' in str(e) or 'UnauthorizedOperation' in str(e):
                        continue
                    else:
                        # For other errors, we'll still include the model but mark it
                        accessible_models.append({
                            'id': model_id,
                            'name': f"{model_name} ({model_id}) - Status Unknown",
                            'provider': model.get('providerName', 'Unknown'),
                            'status': 'UNKNOWN'
                        })
                
        # If no models found with the above method, try a simpler approach
        if not accessible_models:
            # Fallback: Get all models and let user try them
            response = bedrock_client.list_foundation_models()
            
            for model in response.get('modelSummaries', []):
                model_id = model.get('modelId', '')
                model_name = model.get('modelName', '')
                
                # Filter for text generation models
                if (model.get('inputModalities') and 'TEXT' in model.get('inputModalities', []) and
                    model.get('outputModalities') and 'TEXT' in model.get('outputModalities', [])):
                    
                    accessible_models.append({
                        'id': model_id,
                        'name': f"{model_name} ({model_id})",
                        'provider': model.get('providerName', 'Unknown'),
                        'status': 'AVAILABLE'
                    })
        
        return accessible_models
        
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        if error_code == 'AccessDenied':
            st.error("Access denied to Bedrock. Please check your permissions for Amazon Bedrock.")
        elif error_code == 'UnauthorizedOperation':
            st.error("Unauthorized operation. Please ensure you have the necessary Bedrock permissions.")
        else:
            st.error(f"Error fetching Bedrock models: {str(e)}")
        return []
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return []


def get_aws_cli_region():
    """Get AWS CLI default region if available"""
    try:
        result = subprocess.run(['aws', 'configure', 'get', 'region'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        return None
    except:
        return None


def check_aws_cli_available():
    """Check if AWS CLI is available and configured"""
    try:
        result = subprocess.run(['aws', 'configure', 'list'], 
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except:
        return False
