# 📖 Complete Usage Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Smart Query Engine](#smart-query-engine)
3. [Complex Query Processing](#complex-query-processing)
4. [Resource Interaction](#resource-interaction)
5. [Configuration](#configuration)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

## Getting Started

### First Time Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure AWS Access**
   ```bash
   aws configure
   # Enter your AWS credentials and default region
   ```

3. **Choose Your AI Provider**
   - **Ollama (Local)**: `ollama pull llama2`
   - **AWS Bedrock**: Enable models in AWS console

4. **Launch the Application**
   ```bash
   streamlit run ui-app-new.py
   ```

### Initial Configuration

When you first open the app:

1. **Select Theme**: Choose Light or Dark theme in the sidebar
2. **Choose LLM Provider**: Select Ollama or Bedrock
3. **Configure Model**: Select your preferred model
4. **Set AWS Profile**: Choose your AWS profile (usually "default")
5. **Test Connection**: Verify both AI and AWS connections are working

## Smart Query Engine

### What is Smart Query?

The Smart Query Engine analyzes your natural language questions and dynamically collects only the AWS data needed to answer your query. This approach:
- Avoids overwhelming the AI with unnecessary data
- Provides faster responses
- Reduces AWS API calls
- Focuses on relevant information

### How to Use Smart Query

1. **Open the Smart Query Tab**
2. **Enter Your Question** in natural language
3. **Click "⚡ Smart Query"**
4. **Review the Results** with AI analysis

### Example Queries

#### Infrastructure Overview
```
Show me all running EC2 instances
What RDS databases do I have?
List my S3 buckets
```

#### Security Analysis
```
Which security groups allow access from anywhere?
Show me resources without encryption
Find publicly accessible resources
```

#### Cost Optimization
```
What are my most expensive resources?
Show me unused resources
Find resources running in expensive regions
```

#### Operational Insights
```
Which resources are in alarm state?
Show me resources with high CPU usage
List resources without backup enabled
```

### Understanding Smart Query Results

The Smart Query interface shows:
- **Query Analysis**: What services were detected
- **Data Collection Progress**: Real-time collection status
- **AI Analysis**: Structured response with insights
- **Context Preview**: Debug info showing data size and sources

## Complex Query Processing

### Pre-defined Query Templates

The Complex Query tab includes several pre-built query templates:

1. **Running EC2s with Security Groups**
   - Lists all running instances
   - Shows associated security groups
   - Analyzes security posture

2. **RDS Analysis**
   - Database instance details
   - Backup configuration
   - Performance metrics

3. **S3 Bucket Security**
   - Bucket policies
   - Public access settings
   - Encryption status

4. **Cost Analysis**
   - Resource costs by service
   - Trends and recommendations
   - Optimization opportunities

### Custom Structured Queries

You can also write custom queries using a SQL-like syntax:

```sql
SELECT instances, security_groups 
FROM ec2 
WHERE state = 'running' 
AND instance_type LIKE 't3.*'
```

### Visualizations

Complex queries automatically generate:
- **Charts**: Bar charts, pie charts, line graphs
- **Tables**: Structured data display
- **Metrics**: Key performance indicators
- **Trends**: Historical data analysis

### Export Options

Results can be exported in multiple formats:
- **JSON**: Raw data export
- **CSV**: Tabular data for spreadsheets
- **Markdown**: Documentation-ready format

## Resource Interaction

### Individual Resource Analysis

1. **Browse Available Resources**
   - Resources are automatically discovered
   - Organized by service type
   - Shows current status

2. **Select Resources**
   - Use checkboxes to select resources
   - Can select multiple resources
   - Cross-service selection supported

3. **AI Analysis**
   - Click "🔍 Analyze Selected"
   - Get AI-powered insights
   - Receive recommendations

### Resource Comparison

When multiple resources are selected:
- **Similarities**: Common attributes and configurations
- **Differences**: Unique characteristics
- **Recommendations**: Optimization suggestions
- **Best Practices**: Security and cost advice

### Supported Resource Types

- **EC2**: Instances, security groups, key pairs
- **RDS**: Databases, clusters, snapshots
- **S3**: Buckets, objects, policies
- **Lambda**: Functions, layers, triggers
- **VPC**: Networks, subnets, route tables
- **ECS/EKS**: Container services
- **CloudFormation**: Stacks and resources

## Configuration

### LLM Provider Configuration

#### Ollama Setup
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve

# Pull models
ollama pull llama2
ollama pull codellama
ollama pull mistral
```

#### Bedrock Setup
1. **Enable Bedrock** in AWS Console
2. **Request Model Access** for desired models
3. **Verify IAM Permissions** for bedrock:InvokeModel
4. **Test Connection** in the app

### AWS Profile Management

#### Multiple Profiles
```bash
# Create profiles
aws configure --profile dev
aws configure --profile prod
aws configure --profile staging
```

#### Profile Switching
- Use the sidebar dropdown to switch profiles
- Connection status is shown for each profile
- Profile-specific quick stats are displayed

### Advanced Configuration

#### Environment Variables
```bash
# AWS Configuration
export AWS_PROFILE=default
export AWS_DEFAULT_REGION=us-east-1

# Ollama Configuration
export OLLAMA_HOST=localhost:11434
export OLLAMA_MODEL=llama2

# App Configuration
export STREAMLIT_THEME=light
export DEBUG_MODE=false
```

## Best Practices

### Query Optimization

1. **Be Specific**: Use specific service names and attributes
2. **Use Filters**: Add conditions to narrow results
3. **Batch Related Queries**: Group related questions together
4. **Check Data Size**: Monitor context size in debug mode

### Security Best Practices

1. **Use IAM Roles**: Prefer IAM roles over access keys
2. **Least Privilege**: Grant minimal required permissions
3. **Audit Queries**: Review queries before execution
4. **Monitor Usage**: Track API calls and costs

### Performance Tips

1. **Smart Query First**: Use Smart Query for exploratory analysis
2. **Cache Results**: Save frequently used data
3. **Limit Scope**: Focus on specific regions or services
4. **Use Filters**: Apply filters to reduce data volume

## Troubleshooting

### Common Issues

#### Connection Problems

**Error**: "AWS credentials not found"
```bash
# Solution: Configure AWS CLI
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
```

**Error**: "Ollama not available"
```bash
# Solution: Start Ollama service
ollama serve

# Check if running
curl http://localhost:11434/api/tags
```

**Error**: "Bedrock access denied"
- Check IAM permissions
- Verify model access in Bedrock console
- Ensure region supports Bedrock

#### Performance Issues

**Slow Queries**
- Reduce query scope
- Use specific filters
- Check network connectivity
- Monitor AWS API limits

**High Memory Usage**
- Limit data collection
- Use Smart Query instead of full collection
- Restart the application

**Connection Timeouts**
- Check network connectivity
- Verify AWS CLI configuration
- Increase timeout values

#### Data Issues

**Missing Resources**
- Check AWS permissions
- Verify resource existence
- Check region configuration
- Review IAM policy

**Incorrect Data**
- Refresh AWS credentials
- Clear cache
- Check data collection settings
- Verify service availability

### Debug Mode

Enable debug mode for detailed troubleshooting:
```python
# In the app
st.session_state.debug_mode = True
```

Debug mode shows:
- Query analysis steps
- Data collection progress
- API call details
- Error stack traces
- Performance metrics

### Getting Help

1. **Check Logs**: Review Streamlit logs for errors
2. **Enable Debug**: Use debug mode for detailed info
3. **Test Connections**: Verify AWS and AI connections
4. **Review Configuration**: Check all settings
5. **Consult Documentation**: Review API documentation

### Support Resources

- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: Comprehensive guides and references
- **Community**: Connect with other users
- **Examples**: Sample queries and configurations

## Advanced Usage

### Custom Modules

You can extend the application by creating custom modules:

1. **Create Module**: Add to `modules/` directory
2. **Follow Interface**: Implement standard functions
3. **Import Module**: Add to main application
4. **Test Integration**: Verify functionality

### API Integration

The application can be integrated with other systems:

```python
# Example: Automated reporting
from modules.aws_data_manager import collect_aws_data
from modules.bedrock_query_engine import query_bedrock_model

# Collect data
data = collect_aws_data(['ec2', 'rds'], 'production')

# Generate report
report = query_bedrock_model(
    "Create a security report for these resources",
    data,
    "claude-3-sonnet"
)
```

### Batch Processing

For large-scale analysis:

```python
# Process multiple accounts
accounts = ['dev', 'staging', 'prod']
for account in accounts:
    data = collect_aws_data(services, account)
    analysis = process_with_ai(data)
    save_report(analysis, account)
```

This comprehensive guide should help users understand and effectively use all features of the AWS Infrastructure Explainer.
