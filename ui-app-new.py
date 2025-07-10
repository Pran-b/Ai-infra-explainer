import streamlit as st
import plotly.express as px
import json
import os
import tempfile
from pathlib import Path
from datetime import datetime

# Helper function for JSON serialization
def safe_json_display(data, language="json"):
    """Safely display JSON data with datetime handling"""
    def json_serialize(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")
    
    try:
        json_data = json.dumps(data, default=json_serialize, indent=2)
        st.code(json_data, language=language)
    except Exception as e:
        st.error(f"Error displaying JSON: {str(e)}")
        st.write(data)

# Import custom modules
from modules.aws_data_manager import collect_aws_data, get_aws_services_list, get_default_services
from modules.bedrock_manager import get_available_bedrock_models, get_aws_cli_region, check_aws_cli_available, get_aws_profiles, test_aws_profile_connection
from modules.ollama_manager import get_ollama_models, is_ollama_available
from modules.theme_manager import apply_theme
from modules.bedrock_query_engine import query_bedrock_model, test_bedrock_connection
from modules.resource_interaction_manager import resource_manager
from modules.complex_query_processor import complex_query_processor
from modules.dynamic_query_engine import dynamic_query_engine
from qa_engine import query_aws_knowledgebase

# Page configuration
st.set_page_config(page_title="AI Infra Explainer", layout="wide")

st.title("🧠 AI Infra Explainer")

# --- Theme Selection ---
theme = st.sidebar.selectbox("Choose Theme", ["Light", "Dark"])
apply_theme(theme)

# --- LLM Provider Selection ---
llm_provider = st.sidebar.radio("Select LLM Provider", ["Ollama", "Bedrock"])

# --- Ollama Configuration ---
ollama_model = None
if llm_provider == "Ollama":
    with st.sidebar.expander("🔧 Ollama Configuration"):
        if is_ollama_available():
            model_options = get_ollama_models()
            selected_model = st.selectbox("Select Ollama Model", model_options, key="ollama_model")
            if selected_model == "Other":
                ollama_model = st.text_input("Enter Model Name", key="custom_ollama")
            else:
                ollama_model = selected_model
        else:
            st.warning("Ollama not found. Please install Ollama first.")
            ollama_model = st.text_input("Enter Model Name", key="custom_ollama")

# --- Bedrock Configuration ---
bedrock_model = None
aws_access_key = aws_secret_key = aws_region = None
use_cli_creds = False
aws_profile = "default"
if llm_provider == "Bedrock":
    with st.sidebar.expander("🔐 AWS Bedrock Configuration"):
        # AWS Profile Selection (moved to top)
        st.markdown("#### AWS Profile Selection")
        # Get available profiles
        available_profiles = get_aws_profiles()
        
        # Profile selection
        if len(available_profiles) > 1:
            aws_profile = st.selectbox(
                "AWS Profile Name", 
                available_profiles,
                index=0,
                help="Select AWS profile for authentication and credential management."
            )
        else:
            aws_profile = st.text_input(
                "AWS Profile Name", 
                value="default",
                help="Specify AWS profile name (e.g., 'default', 'dev', 'prod'). Used for both CLI and credential management."
            )
        
        # Show available profiles
        if len(available_profiles) > 1:
            st.info(f"Available profiles: {', '.join(available_profiles)}")
        
        # Test AWS profile connection
        if st.button("🔍 Test AWS Profile", key="test_aws_profile"):
            with st.spinner(f"Testing AWS profile '{aws_profile}'..."):
                success, result = test_aws_profile_connection(aws_profile)
                if success:
                    st.success(f"✅ Profile '{aws_profile}' connected successfully!")
                    st.json(result)
                else:
                    st.error(f"❌ Profile '{aws_profile}' connection failed: {result}")
        
        st.markdown("---")
        
        # Credential type selection
        cred_type = st.radio(
            "Choose Credential Type",
            ["AWS CLI Credentials", "Manual Access Keys"],
            key="bedrock_cred_type"
        )
        
        if cred_type == "AWS CLI Credentials":
            st.info(f"Using AWS CLI credentials from profile: **{aws_profile}**")
            aws_region = st.text_input("AWS Region", value="us-east-1", key="aws_region_cli")
            
            # Show AWS CLI status
            cli_region = get_aws_cli_region(aws_profile)
            if cli_region:
                st.success(f"AWS CLI region for profile '{aws_profile}': {cli_region}")
                if not aws_region:
                    aws_region = cli_region
            elif check_aws_cli_available(aws_profile):
                st.info(f"AWS CLI profile '{aws_profile}' is available but no region set")
            else:
                st.warning(f"AWS CLI profile '{aws_profile}' not found or not configured")
            
            use_cli_creds = True
            aws_access_key = aws_secret_key = None
            
        else:  # Manual Access Keys
            st.info("Enter your AWS credentials manually")
            aws_access_key = st.text_input("AWS Access Key ID", key="aws_access_key")
            aws_secret_key = st.text_input("AWS Secret Access Key", type="password", key="aws_secret_key")
            aws_region = st.text_input("AWS Region", value="us-east-1", key="aws_region")
            use_cli_creds = False
        
        # Advanced options
        with st.expander("⚙️ Advanced Options"):
            skip_access_verification = st.checkbox(
                "Skip Access Verification", 
                value=False,
                help="If enabled, shows all available models without testing access. Use this if access verification is failing."
            )
            debug_mode = st.checkbox(
                "Debug Mode", 
                value=False,
                help="Shows debug information for Bedrock responses"
            )
        
        # Store these in session state to make them available outside the expander
        st.session_state["skip_access_verification"] = skip_access_verification
        st.session_state["debug_mode"] = debug_mode
        
        # Information about inference profiles
        st.info("💡 **Tip**: Some newer models (like Claude 3.5 Sonnet) require inference profiles instead of direct model IDs. Enable 'Skip Access Verification' if you have issues.")
        
        # Fetch available models
        if st.button("🔄 Fetch Available Models", key="fetch_models"):
            if use_cli_creds:
                if aws_region:
                    with st.spinner("Fetching Bedrock models..."):
                        available_models = get_available_bedrock_models(
                            aws_region=aws_region, 
                            use_cli_creds=True,
                            skip_access_verification=st.session_state.get("skip_access_verification", False),
                            aws_profile=aws_profile
                        )
                        if available_models:
                            st.session_state["bedrock_models"] = available_models
                            st.success(f"Found {len(available_models)} models")
                            
                            # Show model details
                            with st.expander("📋 Model Details"):
                                for model in available_models:
                                    status_emoji = "✅" if model['status'] == 'ACTIVE' else "❓" if model['status'] == 'UNKNOWN' else "🔄"
                                    st.write(f"{status_emoji} **{model['provider']}**: {model['name']}")
                        else:
                            st.warning("No models found or error occurred")
                else:
                    st.error("Please enter AWS region")
            else:
                if aws_access_key and aws_secret_key and aws_region:
                    with st.spinner("Fetching Bedrock models..."):
                        available_models = get_available_bedrock_models(
                            aws_access_key, aws_secret_key, aws_region, use_cli_creds=False,
                            skip_access_verification=st.session_state.get("skip_access_verification", False),
                            aws_profile=aws_profile
                        )
                        if available_models:
                            st.session_state["bedrock_models"] = available_models
                            st.success(f"Found {len(available_models)} models")
                            
                            # Show model details
                            with st.expander("📋 Model Details"):
                                for model in available_models:
                                    status_emoji = "✅" if model['status'] == 'ACTIVE' else "❓" if model['status'] == 'UNKNOWN' else "🔄"
                                    st.write(f"{status_emoji} **{model['provider']}**: {model['name']}")
                        else:
                            st.warning("No models found or error occurred")
                else:
                    st.error("Please enter AWS credentials first")
        
        # Model selection
        if "bedrock_models" in st.session_state and st.session_state["bedrock_models"]:
            # Dynamic model list from AWS
            model_options = [model['name'] for model in st.session_state["bedrock_models"]]
            model_options.append("Other")
            
            selected_model_name = st.selectbox("Select Bedrock Model", model_options, key="bedrock_model")
            
            if selected_model_name == "Other":
                bedrock_model = st.text_input("Enter Bedrock Model ID", key="custom_bedrock")
            else:
                # Find the model ID for the selected model name
                for model in st.session_state["bedrock_models"]:
                    if model['name'] == selected_model_name:
                        bedrock_model = model['id']
                        break
        else:
            # Fallback to default models if not fetched
            st.info("Click 'Fetch Available Models' to see your available models")
            default_models = [
                "anthropic.claude-3-sonnet-20240229-v1:0",
                "anthropic.claude-3-haiku-20240307-v1:0",
                "amazon.titan-text-lite-v1",
                "amazon.titan-text-express-v1",
                "Other"
            ]
            selected_model = st.selectbox("Select Bedrock Model (Default List)", default_models, key="bedrock_model_default")
            
            if selected_model == "Other":
                bedrock_model = st.text_input("Enter Bedrock Model ID", key="custom_bedrock_default")
            else:
                bedrock_model = selected_model
        
        # Test Bedrock connection
        if bedrock_model and st.button("🔧 Test Bedrock Connection", key="test_bedrock"):
            with st.spinner("Testing Bedrock connection..."):
                if use_cli_creds:
                    success, result = test_bedrock_connection(
                        bedrock_model,
                        aws_region=aws_region,
                        use_cli_creds=True,
                        aws_profile=aws_profile
                    )
                else:
                    success, result = test_bedrock_connection(
                        bedrock_model,
                        aws_access_key=aws_access_key,
                        aws_secret_key=aws_secret_key,
                        aws_region=aws_region,
                        use_cli_creds=False,
                        aws_profile=aws_profile
                    )
                
                if success:
                    st.success(f"✅ Connection successful! Model '{bedrock_model}' is accessible.")
                    if st.session_state.get("debug_mode", False):
                        st.json(result)
                else:
                    st.error(f"❌ Connection failed: {result}")

# --- AWS Data Collection (Optional) ---
st.sidebar.markdown("## � Bulk Data Collection (Optional)")
st.sidebar.info("💡 **New**: Use Smart Query instead to avoid context overload!")

with st.sidebar.expander("🔧 Advanced: Collect All Data"):
    st.markdown("**⚠️ Warning**: Collecting all data may cause context overload")
    selected_services = st.multiselect(
        "Choose AWS Services to Analyze",
        get_aws_services_list(),
        default=get_default_services()
    )
    
    if st.button("📥 Collect All AWS Data"):
        if selected_services:
            collect_aws_data(selected_services)
        else:
            st.error("Please select at least one AWS service")

# --- Main Content Area ---
col1, col2 = st.columns([2, 1])

with col1:
    # Add tabs for different interaction modes
    tab1, tab2, tab3, tab4 = st.tabs(["🧠 Smart Query", "🔍 General Query", "📊 Complex Queries", "🎯 Resource Interaction"])
    
    with tab1:
        st.markdown("### 🧠 Smart Query Engine")
        st.markdown("Ask questions without pre-collecting data. The system will intelligently fetch only the AWS data needed for your specific query.")
        
        # Query suggestions
        st.markdown("#### 💡 Query Suggestions")
        col_sugg1, col_sugg2, col_sugg3 = st.columns(3)
        
        suggestion_queries = [
            "Show me running EC2 instances",
            "List all S3 buckets",
            "What Lambda functions do I have?",
            "Show security groups with open ports",
            "List IAM users and their roles",
            "Show unused EC2 instances",
            "Find expensive resources",
            "Security compliance check",
            "Show VPC resources"
        ]
        
        with col_sugg1:
            for i, suggestion in enumerate(suggestion_queries[:3]):
                if st.button(suggestion, key=f"suggestion_{i}"):
                    st.session_state["smart_query"] = suggestion
        
        with col_sugg2:
            for i, suggestion in enumerate(suggestion_queries[3:6], 3):
                if st.button(suggestion, key=f"suggestion_{i}"):
                    st.session_state["smart_query"] = suggestion
        
        with col_sugg3:
            for i, suggestion in enumerate(suggestion_queries[6:], 6):
                if st.button(suggestion, key=f"suggestion_{i}"):
                    st.session_state["smart_query"] = suggestion
        
        # Smart query input
        smart_query = st.text_area(
            "Ask any question about your AWS infrastructure:",
            value=st.session_state.get("smart_query", ""),
            placeholder="e.g., Show me running EC2 instances with their security groups",
            height=100,
            help="No need to collect data first - the system will fetch only what's needed!"
        )
        
        # Store in session state
        st.session_state["smart_query"] = smart_query
        
        # Show what services will be queried
        if smart_query:
            required_services = dynamic_query_engine.analyze_query_requirements(smart_query)
            st.info(f"🎯 **Services to query**: {', '.join(required_services)}")
            
            # Get dynamic suggestions
            suggestions = dynamic_query_engine.get_query_suggestions(smart_query)
            if suggestions and smart_query.lower() not in [s.lower() for s in suggestions]:
                with st.expander("💭 Related Query Suggestions"):
                    for suggestion in suggestions:
                        if st.button(suggestion, key=f"dynamic_sugg_{suggestion}"):
                            st.session_state["smart_query"] = suggestion
                            st.rerun()
        
        # Query execution buttons
        col_smart1, col_smart2 = st.columns([1, 1])
        
        with col_smart1:
            if st.button("⚡ Smart Query", key="execute_smart_query"):
                if smart_query:
                    with st.spinner("Executing smart query..."):
                        try:
                            # Get AWS profile for data collection
                            query_aws_profile = aws_profile if llm_provider == "Bedrock" else "default"
                            
                            # Collect only required data
                            targeted_data = dynamic_query_engine.collect_targeted_data(smart_query, query_aws_profile)
                            
                            # First try complex query processing
                            complex_results = complex_query_processor.process_complex_query(smart_query, targeted_data)
                            
                            if complex_results['type'] != 'general':
                                st.markdown("### 📋 Structured Results")
                                formatted_results = complex_query_processor.format_results_for_display(complex_results)
                                st.markdown(formatted_results)
                                
                                # Show summary
                                if 'summary' in complex_results:
                                    st.markdown("### 📈 Summary")
                                    summary = complex_results['summary']
                                    if isinstance(summary, dict):
                                        summary_cols = st.columns(len(summary))
                                        for i, (key, value) in enumerate(summary.items()):
                                            with summary_cols[i]:
                                                st.metric(key.replace('_', ' ').title(), value)
                            else:
                                # Fall back to AI analysis
                                from aws_collector import format_data_for_llm
                                text_documents = format_data_for_llm(targeted_data)
                                
                                # Debug: Show context size and preview
                                total_context_size = sum(len(doc) for doc in text_documents)
                                st.info(f"🔍 **Context Debug**: {len(text_documents)} documents, {total_context_size:,} total characters")
                                
                                with st.expander("🔍 Context Preview (First 1000 chars)"):
                                    for i, doc in enumerate(text_documents[:1]):  # Show first document only
                                        st.code(doc[:1000] + "..." if len(doc) > 1000 else doc, language="json")
                                
                                # Query AI
                                if llm_provider == "Ollama" and ollama_model:
                                    response = query_aws_knowledgebase(
                                        smart_query,
                                        text_documents,
                                        embed_model='nomic-embed-text',
                                        llm_model=ollama_model
                                    )
                                elif llm_provider == "Bedrock" and bedrock_model:
                                    if use_cli_creds:
                                        response = query_bedrock_model(
                                            query=smart_query,
                                            text_documents=text_documents,
                                            model_id=bedrock_model,
                                            aws_region=aws_region,
                                            use_cli_creds=True,
                                            debug=st.session_state.get("debug_mode", False),
                                            aws_profile=aws_profile
                                        )
                                    else:
                                        response = query_bedrock_model(
                                            query=smart_query,
                                            text_documents=text_documents,
                                            model_id=bedrock_model,
                                            aws_access_key=aws_access_key,
                                            aws_secret_key=aws_secret_key,
                                            aws_region=aws_region,
                                            use_cli_creds=False,
                                            debug=st.session_state.get("debug_mode", False),
                                            aws_profile=aws_profile
                                        )
                                else:
                                    response = "Please configure your LLM provider first"
                                
                                if response:
                                    st.markdown("### 🎯 AI Analysis Results")
                                    st.write(response)
                            
                            # Show collected data summary
                            with st.expander("📊 Data Collection Summary"):
                                data_summary = {}
                                for service, service_data in targeted_data.items():
                                    if isinstance(service_data, dict) and 'error' not in service_data:
                                        resource_count = 0
                                        for resource_type, resources in service_data.items():
                                            if isinstance(resources, list):
                                                resource_count += len(resources)
                                        data_summary[service] = resource_count
                                    else:
                                        data_summary[service] = "Error"
                                
                                if data_summary:
                                    summary_cols = st.columns(len(data_summary))
                                    for i, (service, count) in enumerate(data_summary.items()):
                                        with summary_cols[i]:
                                            st.metric(f"{service} Resources", count)
                                
                                # Option to view raw data
                                if st.checkbox("Show Raw Data"):
                                    safe_json_display(targeted_data)
                                    
                        except Exception as e:
                            st.error(f"Error during smart query: {str(e)}")
                else:
                    st.error("Please enter a query")
        
        with col_smart2:
            if st.button("🔄 Clear & Refresh", key="clear_smart_query"):
                if "smart_query" in st.session_state:
                    del st.session_state["smart_query"]
                st.success("Query cleared!")
                st.rerun()
        
        # Smart query benefits
        with st.expander("ℹ️ Smart Query Benefits"):
            st.markdown("""
            **🧠 Smart Query Engine automatically:**
            
            - **Analyzes your question** to determine which AWS services are needed
            - **Fetches only relevant data** (no context overload!)
            - **Processes queries faster** with smaller datasets
            - **Reduces API calls** and improves performance
            - **Works without pre-collecting data**
            
            **Examples:**
            - "Show running EC2 instances" → Only fetches EC2 data
            - "List S3 buckets" → Only fetches S3 data  
            - "IAM users and roles" → Only fetches IAM data
            - "Security groups with open ports" → Only fetches EC2 security group data
            
            **Perfect for:**
            - Quick infrastructure checks
            - Targeted resource analysis
            - Avoiding context length limits
            - Fast query execution
            """)
    
    with tab2:
        st.markdown("### 🔍 Query Your Infrastructure")
        
        # Query input
        if "aws_raw_data" in st.session_state:
            # Show context size info for Bedrock users
            if llm_provider == "Bedrock":
                from aws_collector import format_data_for_llm
                text_documents = format_data_for_llm(st.session_state["aws_raw_data"])
                
                # Estimate context size
                total_chars = sum(len(doc) for doc in text_documents)
                estimated_tokens = total_chars // 4  # Rough estimation
            
            if estimated_tokens > 10000:
                st.warning(f"⚠️ **Large context detected** (~{estimated_tokens:,} tokens). If you get 'Input too long' errors, try:")
                st.info("• Ask more specific questions • Enable debug mode • Use fewer AWS services")
            elif estimated_tokens > 5000:
                st.info(f"📊 Context size: ~{estimated_tokens:,} tokens (moderate)")
            else:
                st.success(f"📊 Context size: ~{estimated_tokens:,} tokens (small)")
        
        query = st.text_area(
            "Ask a question about your AWS infrastructure:",
            placeholder="e.g., How many EC2 instances are running? What are my security groups?",
            height=100
        )
        
        # Add context test button for Bedrock
        if llm_provider == "Bedrock" and query:
            col_query, col_test = st.columns([3, 1])
            with col_test:
                if st.button("🔍 Test Context", help="Check if your query will fit within model limits"):
                    from modules.bedrock_query_engine import estimate_tokens
                    
                    # Get fresh text documents
                    from aws_collector import format_data_for_llm
                    text_documents = format_data_for_llm(st.session_state["aws_raw_data"])
                    
                    # Estimate tokens
                    context_tokens = sum(estimate_tokens(doc) for doc in text_documents)
                    query_tokens = estimate_tokens(query)
                    total_tokens = context_tokens + query_tokens + 1000  # Buffer
                    
                    if total_tokens > 8000:
                        st.error(f"❌ Likely too large ({total_tokens:,} tokens). Try a shorter query or fewer services.")
                    else:
                        st.success(f"✅ Should fit ({total_tokens:,} tokens estimated)")
        
        if st.button("🤖 Get AI Analysis"):
            if query:
                with st.spinner("Analyzing your infrastructure..."):
                    try:
                        # Format data for LLM
                        from aws_collector import format_data_for_llm
                        text_documents = format_data_for_llm(st.session_state["aws_raw_data"])
                        
                        # Query the knowledge base
                        if llm_provider == "Ollama" and ollama_model:
                            response = query_aws_knowledgebase(
                                query, 
                                text_documents, 
                                embed_model='nomic-embed-text',
                                llm_model=ollama_model
                            )
                        elif llm_provider == "Bedrock" and bedrock_model:
                            # Use Bedrock for querying
                            if use_cli_creds:
                                response = query_bedrock_model(
                                    query=query,
                                    text_documents=text_documents,
                                    model_id=bedrock_model,
                                    aws_region=aws_region,
                                    use_cli_creds=True,
                                    debug=st.session_state.get("debug_mode", False),
                                    aws_profile=aws_profile
                                )
                            else:
                                response = query_bedrock_model(
                                    query=query,
                                    text_documents=text_documents,
                                    model_id=bedrock_model,
                                    aws_access_key=aws_access_key,
                                    aws_secret_key=aws_secret_key,
                                    aws_region=aws_region,
                                    use_cli_creds=False,
                                    debug=st.session_state.get("debug_mode", False),
                                    aws_profile=aws_profile
                                )
                        else:
                            st.error("Please configure your LLM provider first")
                            response = None
                        
                        if response:
                            st.markdown("### 🎯 AI Analysis Results")
                            st.write(response)                            
                    except Exception as e:
                        st.error(f"Error during analysis: {str(e)}")
            else:
                st.error("Please enter a query")
        else:
            st.info("👆 Please collect AWS data first to start querying")
    
    with tab3:
        st.markdown("### 📊 Complex Structured Queries")
        
        if "aws_raw_data" in st.session_state:
            st.markdown("Run complex queries that extract and analyze specific information from your AWS infrastructure.")
            st.info("💡 **Tip**: Use Smart Query (first tab) to avoid context overload - it fetches only needed data!")
            
            # Pre-defined complex queries
            st.markdown("#### 🚀 Quick Complex Queries")
            
            complex_queries = [
                {
                    "name": "Running EC2s with Security Groups",
                    "query": "Give me a list of running EC2 instances and security groups assigned to them with no duplicates in security groups",
                    "description": "Lists all running EC2 instances with their security groups, showing unique security groups"
                },
                {
                    "name": "Security Group Usage Analysis",
                    "query": "Which security groups are being used and by what resources",
                    "description": "Analyzes security group usage across all resources"
                },
                {
                    "name": "VPC Resource Mapping",
                    "query": "Show me all resources in each VPC",
                    "description": "Groups all resources by VPC for better network understanding"
                },
                {
                    "name": "Cost Analysis Report",
                    "query": "Analyze my infrastructure for cost optimization opportunities",
                    "description": "Identifies high-cost resources and optimization opportunities"
                },
                {
                    "name": "Compliance Check",
                    "query": "Check my infrastructure for compliance issues",
                    "description": "Scans for security and compliance violations"
                },
                {
                    "name": "Unused Resources",
                    "query": "Find unused or idle resources that are wasting money",
                    "description": "Identifies stopped instances, unattached volumes, and other unused resources"
                }
            ]
            
            # Create buttons for quick queries
            col1_queries, col2_queries = st.columns(2)
            
            with col1_queries:
                for i, query_info in enumerate(complex_queries[:3]):
                    if st.button(f"🔍 {query_info['name']}", key=f"complex_query_{i}"):
                        st.session_state["complex_query"] = query_info['query']
                        st.session_state["complex_query_description"] = query_info['description']
            
            with col2_queries:
                for i, query_info in enumerate(complex_queries[3:], 3):
                    if st.button(f"🔍 {query_info['name']}", key=f"complex_query_{i}"):
                        st.session_state["complex_query"] = query_info['query']
                        st.session_state["complex_query_description"] = query_info['description']
            
            # Custom complex query input
            st.markdown("#### ✏️ Custom Complex Query")
            
            # Show selected query description
            if "complex_query_description" in st.session_state:
                st.info(f"💡 {st.session_state['complex_query_description']}")
            
            complex_query = st.text_area(
                "Enter your complex query:",
                value=st.session_state.get("complex_query", ""),
                placeholder="e.g., Give me a list of running EC2 instances and security groups assigned to them with no duplicates in security groups",
                height=100,
                help="Use natural language to describe complex queries about your infrastructure"
            )
            
            # Store in session state
            st.session_state["complex_query"] = complex_query
            
            # Query processing buttons
            col_process, col_ai = st.columns([1, 1])
            
            with col_process:
                if st.button("⚡ Process Structured Query"):
                    if complex_query:
                        with st.spinner("Processing complex query..."):
                            try:
                                # Process with complex query processor
                                results = complex_query_processor.process_complex_query(
                                    complex_query, 
                                    st.session_state["aws_raw_data"]
                                )
                                
                                if results['type'] != 'general':
                                    st.markdown("### 📋 Structured Results")
                                    
                                    # Display formatted results
                                    formatted_results = complex_query_processor.format_results_for_display(results)
                                    st.markdown(formatted_results)
                                    
                                    # Show raw data if requested
                                    with st.expander("📊 Raw Data"):
                                        safe_json_display(results)
                                    
                                    # Add visualization for certain query types
                                    if results['type'] == 'ec2_with_security_groups':
                                        st.markdown("### 📊 Visualizations")
                                        
                                        # Create charts
                                        col_chart1, col_chart2 = st.columns(2)
                                        
                                        with col_chart1:
                                            # Instance state distribution
                                            state_counts = {}
                                            for instance in results['data']:
                                                state = instance['state']
                                                state_counts[state] = state_counts.get(state, 0) + 1
                                            
                                            if state_counts:
                                                fig = px.pie(
                                                    values=list(state_counts.values()),
                                                    names=list(state_counts.keys()),
                                                    title="Instance State Distribution"
                                                )
                                                st.plotly_chart(fig, use_container_width=True)
                                        
                                        with col_chart2:
                                            # Security groups per instance
                                            sg_counts = [len(instance['security_groups']) for instance in results['data']]
                                            instance_ids = [instance['instance_id'] for instance in results['data']]
                                            
                                            if sg_counts:
                                                fig = px.bar(
                                                    x=instance_ids,
                                                    y=sg_counts,
                                                    title="Security Groups per Instance"
                                                )
                                                fig.update_xaxes(title="Instance ID")
                                                fig.update_yaxes(title="Number of Security Groups")
                                                st.plotly_chart(fig, use_container_width=True)
                                    
                                    elif results['type'] == 'cost_analysis':
                                        st.markdown("### 💰 Cost Visualizations")
                                        
                                        # Cost tier distribution
                                        cost_tiers = {}
                                        for instance in results['data']['ec2_instances']:
                                            tier = instance['cost_tier']
                                            cost_tiers[tier] = cost_tiers.get(tier, 0) + 1
                                        
                                        if cost_tiers:
                                            fig = px.pie(
                                                values=list(cost_tiers.values()),
                                                names=list(cost_tiers.keys()),
                                                title="Cost Tier Distribution",
                                                color_discrete_map={'HIGH': 'red', 'MEDIUM': 'orange', 'LOW': 'green'}
                                            )
                                            st.plotly_chart(fig, use_container_width=True)
                                    
                                    elif results['type'] == 'compliance_check':
                                        st.markdown("### 🔐 Compliance Visualizations")
                                        
                                        # Severity distribution
                                        severity_counts = {}
                                        for issue in results['data']:
                                            severity = issue['severity']
                                            severity_counts[severity] = severity_counts.get(severity, 0) + 1
                                        
                                        if severity_counts:
                                            fig = px.bar(
                                                x=list(severity_counts.keys()),
                                                y=list(severity_counts.values()),
                                                title="Compliance Issues by Severity",
                                                color=list(severity_counts.keys()),
                                                color_discrete_map={'HIGH': 'red', 'MEDIUM': 'orange', 'LOW': 'yellow'}
                                            )
                                            st.plotly_chart(fig, use_container_width=True)
                                else:
                                    st.info("Query not recognized as a structured query. Use 'AI Analysis' for general queries.")
                                    
                            except Exception as e:
                                st.error(f"Error processing complex query: {str(e)}")
                    else:
                        st.error("Please enter a query")
            
            with col_ai:
                if st.button("🤖 AI Analysis"):
                    if complex_query:
                        with st.spinner("Getting AI analysis..."):
                            try:
                                # First try structured processing
                                results = complex_query_processor.process_complex_query(
                                    complex_query, 
                                    st.session_state["aws_raw_data"]
                                )
                                
                                if results['type'] != 'general':
                                    # Use structured results as context for AI
                                    formatted_results = complex_query_processor.format_results_for_display(results)
                                    
                                    ai_prompt = f"""Based on the following structured analysis of AWS infrastructure:

{formatted_results}

Original Query: {complex_query}

Please provide additional insights, recommendations, and explanations about these results. Focus on:
1. What these results mean for the infrastructure
2. Potential security, cost, or performance implications
3. Recommended next steps or actions
4. Best practices related to these findings"""
                                    
                                    # Query AI with structured results
                                    if llm_provider == "Ollama" and ollama_model:
                                        ai_response = query_aws_knowledgebase(
                                            ai_prompt,
                                            [formatted_results],
                                            embed_model='nomic-embed-text',
                                            llm_model=ollama_model
                                        )
                                    elif llm_provider == "Bedrock" and bedrock_model:
                                        if use_cli_creds:
                                            ai_response = query_bedrock_model(
                                                query=ai_prompt,
                                                text_documents=[formatted_results],
                                                model_id=bedrock_model,
                                                aws_region=aws_region,
                                                use_cli_creds=True,
                                                debug=st.session_state.get("debug_mode", False),
                                                aws_profile=aws_profile
                                            )
                                        else:
                                            ai_response = query_bedrock_model(
                                                query=ai_prompt,
                                                text_documents=[formatted_results],
                                                model_id=bedrock_model,
                                                aws_access_key=aws_access_key,
                                                aws_secret_key=aws_secret_key,
                                                aws_region=aws_region,
                                                use_cli_creds=False,
                                                debug=st.session_state.get("debug_mode", False),
                                                aws_profile=aws_profile
                                            )
                                    else:
                                        ai_response = "Please configure your LLM provider first"
                                    
                                    if ai_response:
                                        st.markdown("### 🎯 AI Analysis & Recommendations")
                                        st.write(ai_response)
                                        
                                        # Also show structured results
                                        with st.expander("📋 Structured Data"):
                                            st.markdown(formatted_results)
                                else:
                                    # Fall back to regular AI query
                                    from aws_collector import format_data_for_llm
                                    text_documents = format_data_for_llm(st.session_state["aws_raw_data"])
                                    
                                    if llm_provider == "Ollama" and ollama_model:
                                        ai_response = query_aws_knowledgebase(
                                            complex_query,
                                            text_documents,
                                            embed_model='nomic-embed-text',
                                            llm_model=ollama_model
                                        )
                                    elif llm_provider == "Bedrock" and bedrock_model:
                                        if use_cli_creds:
                                            ai_response = query_bedrock_model(
                                                query=complex_query,
                                                text_documents=text_documents,
                                                model_id=bedrock_model,
                                                aws_region=aws_region,
                                                use_cli_creds=True,
                                                debug=st.session_state.get("debug_mode", False),
                                                aws_profile=aws_profile
                                            )
                                        else:
                                            ai_response = query_bedrock_model(
                                                query=complex_query,
                                                text_documents=text_documents,
                                                model_id=bedrock_model,
                                                aws_access_key=aws_access_key,
                                                aws_secret_key=aws_secret_key,
                                                aws_region=aws_region,
                                                use_cli_creds=False,
                                                debug=st.session_state.get("debug_mode", False),
                                                aws_profile=aws_profile
                                            )
                                    else:
                                        ai_response = "Please configure your LLM provider first"
                                    
                                    if ai_response:
                                        st.markdown("### 🎯 AI Analysis Results")
                                        st.write(ai_response)
                                        
                            except Exception as e:
                                st.error(f"Error during AI analysis: {str(e)}")
                    else:
                        st.error("Please enter a query")
            
            # Export options
            st.markdown("### 📥 Export Options")
            col_export1, col_export2, col_export3 = st.columns(3)
            
            with col_export1:
                if st.button("📄 Export as JSON"):
                    json_data = json.dumps(results, indent=2, default=str)
                    st.download_button(
                        label="Download JSON",
                        data=json_data,
                        file_name=f"aws_query_results_{results['type']}.json",
                        mime="application/json"
                    )
            
            with col_export2:
                if st.button("📊 Export as CSV") and results['type'] == 'ec2_with_security_groups':
                    # Convert to CSV format
                    csv_data = []
                    for instance in results['data']:
                        for sg in instance['security_groups']:
                            csv_data.append({
                                'Instance ID': instance['instance_id'],
                                'Instance Type': instance['instance_type'],
                                'State': instance['state'],
                                'Security Group ID': sg['id'],
                                'Security Group Name': sg['name'],
                                'Public IP': instance['public_ip'],
                                'Private IP': instance['private_ip'],
                                'VPC ID': instance['vpc_id'],
                                'Subnet ID': instance['subnet_id']
                            })
                    
                    if csv_data:
                        import pandas as pd
                        df = pd.DataFrame(csv_data)
                        csv_string = df.to_csv(index=False)
                        st.download_button(
                            label="Download CSV",
                            data=csv_string,
                            file_name=f"aws_ec2_security_groups.csv",
                            mime="text/csv"
                        )
            
            with col_export3:
                if st.button("📝 Export as Markdown"):
                    markdown_data = complex_query_processor.format_results_for_display(results)
                    st.download_button(
                        label="Download Markdown",
                        data=markdown_data,
                        file_name=f"aws_query_results_{results['type']}.md",
                        mime="text/markdown"
                    )
        else:
            st.info("👆 Please collect AWS data first to run complex queries")
            st.warning("⚠️ **Avoid Context Overload**: Consider using Smart Query (first tab) instead - it fetches only the data needed for your specific query!")
    
    with tab4:
        st.markdown("### 🎯 Interact with Individual Resources")
        
        if "aws_raw_data" in st.session_state:
            # Extract individual resources
            resources = resource_manager.extract_individual_resources(st.session_state["aws_raw_data"])
            
            if resources:
                # Resource selection interface
                st.markdown("#### Select Resources to Interact With")
                
                selected_resources = []
                
                # Create expandable sections for each service
                for service, resource_types in resources.items():
                    with st.expander(f"📦 {service} Resources"):
                        for resource_type, resource_list in resource_types.items():
                            st.markdown(f"**{resource_type.title()}** ({len(resource_list)} items)")
                            
                            # Create checkboxes for each resource
                            for i, resource in enumerate(resource_list):
                                resource_summary = resource_manager.get_resource_summary(resource, resource_type)
                                
                                # Create unique key for checkbox
                                checkbox_key = f"{service}_{resource_type}_{i}"
                                
                                col_check, col_actions = st.columns([3, 1])
                                
                                with col_check:
                                    if st.checkbox(resource_summary, key=checkbox_key):
                                        selected_resources.append((service, resource_type, i))
                                
                                with col_actions:
                                    # Quick actions menu
                                    actions = resource_manager.get_resource_actions(resource_type)
                                    if st.selectbox("Quick Action", ["Select action..."] + actions, key=f"action_{checkbox_key}") != "Select action...":
                                        selected_action = st.selectbox("Quick Action", ["Select action..."] + actions, key=f"action_{checkbox_key}")
                                        if selected_action != "Select action...":
                                            # Auto-populate query based on selected action
                                            st.session_state[f"resource_query_{checkbox_key}"] = f"Please {selected_action.lower()} for this resource"
                                
                                # Show recommendations
                                recommendations = resource_manager.create_resource_recommendations(resource, resource_type)
                                if recommendations:
                                    with st.expander(f"💡 Recommendations"):
                                        for rec in recommendations:
                                            st.write(rec)
                
                # Query interface for selected resources
                if selected_resources:
                    st.markdown(f"#### Query Selected Resources ({len(selected_resources)} selected)")
                    
                    # Pre-defined queries
                    st.markdown("**Quick Questions:**")
                    quick_questions = [
                        "What is the current security posture of these resources?",
                        "What are the cost optimization opportunities?",
                        "Are there any compliance issues?",
                        "What are the performance characteristics?",
                        "Are there any security risks?",
                        "What backup and recovery options are available?",
                        "How can I improve the configuration?",
                        "What are the dependencies between these resources?"
                    ]
                    
                    col_q1, col_q2 = st.columns(2)
                    with col_q1:
                        for i, question in enumerate(quick_questions[:4]):
                            if st.button(question, key=f"quick_q_{i}"):
                                st.session_state["resource_query"] = question
                    
                    with col_q2:
                        for i, question in enumerate(quick_questions[4:], 4):
                            if st.button(question, key=f"quick_q_{i}"):
                                st.session_state["resource_query"] = question
                    
                    # Custom query input
                    resource_query = st.text_area(
                        "Custom Question about Selected Resources:",
                        value=st.session_state.get("resource_query", ""),
                        placeholder="e.g., How secure are these resources? What optimizations can be made?",
                        height=100,
                        key="resource_query_input"
                    )
                    
                    # Update session state
                    st.session_state["resource_query"] = resource_query
                    
                    # Query button
                    col_analyze, col_compare = st.columns([1, 1])
                    
                    with col_analyze:
                        if st.button("🤖 Analyze Selected Resources"):
                            if resource_query:
                                with st.spinner("Analyzing selected resources..."):
                                    try:
                                        # Prepare model configuration
                                        model_config = {
                                            'model_name': ollama_model,
                                            'model_id': bedrock_model,
                                            'aws_region': aws_region,
                                            'aws_access_key': aws_access_key,
                                            'aws_secret_key': aws_secret_key,
                                            'use_cli_creds': use_cli_creds if llm_provider == "Bedrock" else False,
                                            'debug': st.session_state.get("debug_mode", False),
                                            'aws_profile': aws_profile if llm_provider == "Bedrock" else None
                                        }
                                        
                                        # Query selected resources
                                        response = resource_manager.query_resources(
                                            resource_query,
                                            selected_resources,
                                            st.session_state["aws_raw_data"],
                                            llm_provider,
                                            model_config
                                        )
                                        
                                        if response:
                                            st.markdown("### 🎯 Resource Analysis Results")
                                            st.write(response)
                                            
                                            # Show selected resources context
                                            with st.expander("📋 Selected Resources Context"):
                                                context = resource_manager.create_resource_context(
                                                    selected_resources, 
                                                    st.session_state["aws_raw_data"]
                                                )
                                                st.code(context, language="json")
                                        else:
                                            st.error("No response received from AI model")
                                            
                                    except Exception as e:
                                        st.error(f"Error during resource analysis: {str(e)}")
                            else:
                                st.error("Please enter a question about the selected resources")
                    
                    with col_compare:
                        if st.button("⚖️ Compare Resources") and len(selected_resources) == 2:
                            # Compare exactly 2 resources
                            service1, resource_type1, index1 = selected_resources[0]
                            service2, resource_type2, index2 = selected_resources[1]
                            
                            if resource_type1 == resource_type2:
                                with st.spinner("Comparing resources..."):
                                    try:
                                        resources_data = resource_manager.extract_individual_resources(st.session_state["aws_raw_data"])
                                        resource1 = resources_data[service1][resource_type1][index1]
                                        resource2 = resources_data[service2][resource_type2][index2]
                                        
                                        comparison_context = resource_manager.compare_resources(resource1, resource2, resource_type1)
                                        
                                        # Prepare model configuration
                                        model_config = {
                                            'model_name': ollama_model,
                                            'model_id': bedrock_model,
                                            'aws_region': aws_region,
                                            'aws_access_key': aws_access_key,
                                            'aws_secret_key': aws_secret_key,
                                            'use_cli_creds': use_cli_creds if llm_provider == "Bedrock" else False,
                                            'debug': st.session_state.get("debug_mode", False),
                                            'aws_profile': aws_profile if llm_provider == "Bedrock" else None
                                        }
                                        
                                        # Query for comparison
                                        if llm_provider == "Ollama":
                                            response = query_aws_knowledgebase(
                                                comparison_context,
                                                [comparison_context],
                                                embed_model='nomic-embed-text',
                                                llm_model=model_config.get('model_name')
                                            )
                                        elif llm_provider == "Bedrock":
                                            response = query_bedrock_model(
                                                query=comparison_context,
                                                text_documents=[comparison_context],
                                                model_id=model_config.get('model_id'),
                                                aws_region=model_config.get('aws_region'),
                                                aws_access_key=model_config.get('aws_access_key'),
                                                aws_secret_key=model_config.get('aws_secret_key'),
                                                use_cli_creds=model_config.get('use_cli_creds', False),
                                                debug=model_config.get('debug', False),
                                                aws_profile=model_config.get('aws_profile')
                                            )
                                        
                                        if response:
                                            st.markdown("### ⚖️ Resource Comparison Results")
                                            st.write(response)
                                        else:
                                            st.error("No comparison response received")
                                            
                                    except Exception as e:
                                        st.error(f"Error during comparison: {str(e)}")
                            else:
                                st.error("Resources must be of the same type to compare")
                        elif len(selected_resources) != 2:
                            st.info("Select exactly 2 resources to compare")
                else:
                    st.info("👆 Select resources above to interact with them")
            else:
                st.info("No resources found in collected data")
        else:
            st.info("👆 Please collect AWS data first to interact with resources")

with col2:
    st.markdown("### 📊 Infrastructure Overview")
    
    if "aws_raw_data" in st.session_state:
        # Show summary statistics
        aws_data = st.session_state["aws_raw_data"]
        
        # Count resources
        resource_counts = {}
        for service, data in aws_data.items():
            if isinstance(data, dict) and 'error' not in data:
                total_resources = 0
                for resource_type, resources in data.items():
                    if isinstance(resources, list):
                        total_resources += len(resources)
                resource_counts[service] = total_resources
        
        # Display metrics
        if resource_counts:
            st.markdown("#### Resource Summary")
            for service, count in resource_counts.items():
                st.metric(f"{service} Resources", count)
        
        # Show raw data in expandable section
        with st.expander("🔍 Raw Data"):
            safe_json_display(aws_data)
    else:
        st.info("No data collected yet")

# --- Export Options ---
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📤 Export Summary"):
        st.success("Export functionality coming soon!")

with col2:
    if st.button("📊 Generate Report"):
        st.success("Report generation coming soon!")

with col3:
    if st.button("🔄 Refresh Data"):
        if "aws_raw_data" in st.session_state:
            del st.session_state["aws_raw_data"]
        if "bedrock_models" in st.session_state:
            del st.session_state["bedrock_models"]
        st.success("Data cleared! Please collect AWS data again.")
        st.rerun()
