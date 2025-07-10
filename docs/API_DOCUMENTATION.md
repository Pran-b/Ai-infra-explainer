# API Documentation

## Module Overview

The AWS Infrastructure Explainer is built with a modular architecture for maintainability and extensibility.

### Core Modules

#### 1. AWS Data Manager (`modules/aws_data_manager.py`)
Handles all AWS data collection operations.

**Key Functions:**
- `collect_aws_data(services, profile_name)`: Collects data from specified AWS services
- `get_aws_services_list()`: Returns list of supported AWS services
- `get_default_services()`: Returns default services for quick collection

**Supported Services:**
- EC2 (instances, security groups, key pairs)
- RDS (instances, clusters, snapshots)
- S3 (buckets, objects)
- Lambda (functions, layers)
- ECS (clusters, services, tasks)
- EKS (clusters, node groups)
- CloudFormation (stacks, resources)
- IAM (users, roles, policies)
- CloudWatch (alarms, metrics)
- VPC (VPCs, subnets, route tables)
- ELB (load balancers)
- Route53 (hosted zones, records)
- SNS (topics, subscriptions)
- SQS (queues)
- DynamoDB (tables)

#### 2. Bedrock Manager (`modules/bedrock_manager.py`)
Manages AWS Bedrock model integration.

**Key Functions:**
- `get_available_bedrock_models()`: Lists available Bedrock models
- `test_bedrock_connection()`: Tests connection to Bedrock
- `get_aws_profiles()`: Gets available AWS profiles
- `check_aws_cli_available()`: Checks if AWS CLI is configured

#### 3. Ollama Manager (`modules/ollama_manager.py`)
Manages local Ollama model integration.

**Key Functions:**
- `get_ollama_models()`: Lists available Ollama models
- `is_ollama_available()`: Checks if Ollama is running
- `test_ollama_connection()`: Tests connection to Ollama

#### 4. Dynamic Query Engine (`modules/dynamic_query_engine.py`)
Implements smart query processing with dynamic data collection.

**Key Functions:**
- `dynamic_query_engine(query, profile_name, llm_provider, model_name)`: Processes queries intelligently
- `analyze_query_requirements()`: Analyzes what AWS services are needed for a query
- `collect_relevant_data()`: Collects only necessary data based on query

#### 5. Complex Query Processor (`modules/complex_query_processor.py`)
Handles structured queries with visualizations.

**Key Functions:**
- `complex_query_processor()`: Main processing function for complex queries
- `create_visualizations()`: Creates charts and graphs from query results
- `export_results()`: Exports results in various formats

#### 6. Resource Interaction Manager (`modules/resource_interaction_manager.py`)
Manages resource-level analysis and comparison.

**Key Functions:**
- `resource_manager()`: Main resource interaction interface
- `analyze_resource()`: Analyzes individual AWS resources
- `compare_resources()`: Compares multiple resources

### Usage Examples

#### Basic AWS Data Collection
```python
from modules.aws_data_manager import collect_aws_data

# Collect EC2 and RDS data
services = ['ec2', 'rds']
data = collect_aws_data(services, profile_name='default')
```

#### Smart Query Processing
```python
from modules.dynamic_query_engine import dynamic_query_engine

# Process a natural language query
query = "Show me running EC2 instances with high CPU usage"
result = dynamic_query_engine(
    query=query,
    profile_name='default',
    llm_provider='Ollama',
    model_name='llama2'
)
```

#### Resource Analysis
```python
from modules.resource_interaction_manager import analyze_resource

# Analyze specific EC2 instance
resource_data = {...}  # Resource data from AWS
analysis = analyze_resource(resource_data, 'ec2-instance')
```

## Configuration

### Environment Variables
```bash
# AWS Configuration
AWS_PROFILE=default
AWS_DEFAULT_REGION=us-east-1

# Ollama Configuration (optional)
OLLAMA_HOST=localhost:11434
```

### AWS Permissions
The application requires the following AWS permissions:
- `ec2:Describe*`
- `rds:Describe*`
- `s3:List*`
- `s3:Get*`
- `lambda:List*`
- `lambda:Get*`
- `ecs:List*`
- `ecs:Describe*`
- `eks:List*`
- `eks:Describe*`
- `cloudformation:List*`
- `cloudformation:Describe*`
- `iam:List*`
- `iam:Get*`
- `cloudwatch:List*`
- `cloudwatch:Get*`
- `cloudwatch:Describe*`
- `bedrock:InvokeModel` (for Bedrock)
- `bedrock:ListFoundationModels` (for Bedrock)

## Error Handling

### Common Errors

#### AWS Configuration Issues
- **Error**: `NoCredentialsError`
- **Solution**: Configure AWS CLI or set environment variables
- **Code**: Check with `check_aws_cli_available()`

#### Ollama Connection Issues
- **Error**: `ConnectionError`
- **Solution**: Ensure Ollama is running (`ollama serve`)
- **Code**: Check with `is_ollama_available()`

#### Bedrock Access Issues
- **Error**: `AccessDeniedError`
- **Solution**: Ensure Bedrock access is enabled and models are available
- **Code**: Test with `test_bedrock_connection()`

### Debugging

Enable debug mode by setting:
```python
st.session_state.debug_mode = True
```

This will show:
- Query analysis details
- Data collection progress
- LLM prompt construction
- Response processing steps

## Extension Points

### Adding New AWS Services
1. Add service to `get_aws_services_list()` in `aws_data_manager.py`
2. Implement collection function following the pattern
3. Add service-specific error handling
4. Update documentation

### Adding New LLM Providers
1. Create new manager module (e.g., `modules/openai_manager.py`)
2. Implement standard interface functions
3. Add to UI provider selection
4. Update configuration documentation

### Custom Query Types
1. Add new query patterns to `dynamic_query_engine.py`
2. Implement specific processing logic
3. Add visualization support if needed
4. Update user documentation
