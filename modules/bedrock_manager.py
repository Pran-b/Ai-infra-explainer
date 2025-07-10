import boto3
import json
import subprocess
import streamlit as st
from botocore.exceptions import ClientError


def get_available_bedrock_models(aws_access_key=None, aws_secret_key=None, aws_region=None, use_cli_creds=False, skip_access_verification=False, aws_profile=None):
    """Fetch available Bedrock models and inference profiles with access granted based on AWS credentials"""
    try:
        # Create Bedrock client with provided credentials or CLI credentials
        if use_cli_creds:
            # Use AWS CLI credentials (specified profile or default profile)
            if aws_profile and aws_profile != "default":
                session = boto3.Session(profile_name=aws_profile)
                bedrock_client = session.client('bedrock', region_name=aws_region or 'us-east-1')
            else:
                bedrock_client = boto3.client('bedrock', region_name=aws_region or 'us-east-1')
        else:
            # Use provided access key and secret key
            bedrock_client = boto3.client(
                'bedrock',
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=aws_region
            )
        
        accessible_models = []
        
        # Get foundation models
        response = bedrock_client.list_foundation_models(
            byOutputModality='TEXT',  # Filter for text output models
            byInferenceType='ON_DEMAND'  # Filter for on-demand inference models
        )
        
        # Try to get inference profiles (this is a newer feature)
        try:
            inference_profiles_response = bedrock_client.list_inference_profiles()
            inference_profiles = inference_profiles_response.get('inferenceProfileSummaries', [])
        except Exception as e:
            st.info("Inference profiles not available in this region or with current permissions")
            inference_profiles = []
        
        # Process inference profiles first (these are preferred for newer models)
        for profile in inference_profiles:
            profile_id = profile.get('inferenceProfileId', '')
            profile_name = profile.get('inferenceProfileName', '')
            status = profile.get('status', 'UNKNOWN')
            
            # Filter for text-capable profiles
            if profile.get('type') == 'SYSTEM_DEFINED' and status == 'ACTIVE':
                # If skipping access verification, just add all profiles
                if skip_access_verification:
                    accessible_models.append({
                        'id': profile_id,
                        'name': f"{profile_name} (Inference Profile)",
                        'provider': 'System Defined',
                        'status': 'AVAILABLE',
                        'type': 'inference_profile'
                    })
                    continue
                
                # Test access to the inference profile
                try:
                    # Create a bedrock runtime client to test profile access
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
                    
                    # Test with a minimal request - assume it's Anthropic-compatible for inference profiles
                    test_body = {
                        "anthropic_version": "bedrock-2023-05-31",
                        "max_tokens": 10,
                        "messages": [{"role": "user", "content": "Hi"}]
                    }
                    
                    # Try to invoke the inference profile
                    bedrock_runtime.invoke_model(
                        body=json.dumps(test_body),
                        modelId=profile_id,
                        accept='application/json',
                        contentType='application/json'
                    )
                    
                    # If we get here, the profile is accessible
                    accessible_models.append({
                        'id': profile_id,
                        'name': f"{profile_name} (Inference Profile)",
                        'provider': 'System Defined',
                        'status': 'ACTIVE',
                        'type': 'inference_profile'
                    })
                    
                except ClientError as e:
                    error_code = e.response.get('Error', {}).get('Code', '')
                    # If it's specifically an access denied error, skip this profile
                    if error_code in ['AccessDeniedException', 'UnauthorizedOperation', 'ValidationException']:
                        continue
                    else:
                        # For other errors, we'll still include the profile but mark it as unknown
                        accessible_models.append({
                            'id': profile_id,
                            'name': f"{profile_name} (Inference Profile) - Access Unknown",
                            'provider': 'System Defined',
                            'status': 'UNKNOWN',
                            'type': 'inference_profile'
                        })
                except Exception as e:
                    # Skip profiles that cause other errors, but log for debugging
                    print(f"Error testing access for inference profile {profile_id}: {e}")
                    continue
        
        # Process foundation models
        for model in response.get('modelSummaries', []):
            model_id = model.get('modelId', '')
            model_name = model.get('modelName', '')
            
            # Filter for text generation models
            if (model.get('inputModalities') and 'TEXT' in model.get('inputModalities', []) and
                model.get('outputModalities') and 'TEXT' in model.get('outputModalities', [])):
                
                # If skipping access verification, just add all models
                if skip_access_verification:
                    accessible_models.append({
                        'id': model_id,
                        'name': f"{model_name} ({model_id})",
                        'provider': model.get('providerName', 'Unknown'),
                        'status': 'AVAILABLE',
                        'type': 'foundation_model'
                    })
                    continue
                
                # Check if model access is granted by trying to invoke it with a test query
                try:
                    # Create a bedrock runtime client to test model access
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
                    
                    # Test with a minimal request to verify access
                    if "anthropic.claude" in model_id:
                        test_body = {
                            "anthropic_version": "bedrock-2023-05-31",
                            "max_tokens": 10,
                            "messages": [{"role": "user", "content": "Hi"}]
                        }
                    elif "amazon.titan" in model_id:
                        test_body = {
                            "inputText": "Hi",
                            "textGenerationConfig": {"maxTokenCount": 10}
                        }
                    elif "ai21.j2" in model_id:
                        test_body = {
                            "prompt": "Hi",
                            "maxTokens": 10
                        }
                    elif "cohere.command" in model_id:
                        test_body = {
                            "prompt": "Hi",
                            "max_tokens": 10
                        }
                    else:
                        # For unknown models, don't test access - just include them
                        accessible_models.append({
                            'id': model_id,
                            'name': f"{model_name} ({model_id}) - Access Not Verified",
                            'provider': model.get('providerName', 'Unknown'),
                            'status': 'UNKNOWN',
                            'type': 'foundation_model'
                        })
                        continue
                    
                    # Try to invoke the model
                    bedrock_runtime.invoke_model(
                        body=json.dumps(test_body),
                        modelId=model_id,
                        accept='application/json',
                        contentType='application/json'
                    )
                    
                    # If we get here, the model is accessible
                    accessible_models.append({
                        'id': model_id,
                        'name': f"{model_name} ({model_id})",
                        'provider': model.get('providerName', 'Unknown'),
                        'status': 'ACTIVE',
                        'type': 'foundation_model'
                    })
                    
                except ClientError as e:
                    error_code = e.response.get('Error', {}).get('Code', '')
                    # If it's specifically an access denied error, skip this model
                    if error_code in ['AccessDeniedException', 'UnauthorizedOperation', 'ValidationException']:
                        continue
                    else:
                        # For other errors, we'll still include the model but mark it as unknown
                        accessible_models.append({
                            'id': model_id,
                            'name': f"{model_name} ({model_id}) - Access Unknown",
                            'provider': model.get('providerName', 'Unknown'),
                            'status': 'UNKNOWN',
                            'type': 'foundation_model'
                        })
                except Exception as e:
                    # Skip models that cause other errors, but log for debugging
                    print(f"Error testing access for model {model_id}: {e}")
                    continue
                
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
                        'status': 'AVAILABLE',
                        'type': 'foundation_model'
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


def get_aws_cli_region(aws_profile=None):
    """Get AWS CLI region for specified profile"""
    try:
        if aws_profile and aws_profile != "default":
            result = subprocess.run(['aws', 'configure', 'get', 'region', '--profile', aws_profile], 
                                  capture_output=True, text=True, timeout=5)
        else:
            result = subprocess.run(['aws', 'configure', 'get', 'region'], 
                                  capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        return None
    except:
        return None


def check_aws_cli_available(aws_profile=None):
    """Check if AWS CLI is available and profile is configured"""
    try:
        if aws_profile and aws_profile != "default":
            result = subprocess.run(['aws', 'configure', 'list', '--profile', aws_profile], 
                                  capture_output=True, text=True, timeout=5)
        else:
            result = subprocess.run(['aws', 'configure', 'list'], 
                                  capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except:
        return False


def get_aws_profiles():
    """Get list of available AWS profiles"""
    try:
        result = subprocess.run(['aws', 'configure', 'list-profiles'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            profiles = result.stdout.strip().split('\n')
            return [profile.strip() for profile in profiles if profile.strip()]
        return ["default"]
    except:
        return ["default"]


def test_aws_profile_connection(aws_profile=None):
    """Test AWS profile connection"""
    try:
        if aws_profile and aws_profile != "default":
            session = boto3.Session(profile_name=aws_profile)
            sts_client = session.client('sts')
        else:
            sts_client = boto3.client('sts')
        
        # Try to get caller identity
        response = sts_client.get_caller_identity()
        return True, {
            'Account': response.get('Account'),
            'UserId': response.get('UserId'),
            'Arn': response.get('Arn')
        }
    except Exception as e:
        return False, str(e)
