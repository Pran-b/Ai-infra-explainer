#!/usr/bin/env python3
"""
Demo script for AWS Infrastructure Explainer
This script demonstrates the core functionality without requiring the UI
"""

import json
import sys
import os
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from modules.aws_data_manager import collect_aws_data, get_aws_services_list
from modules.bedrock_manager import check_aws_cli_available, get_aws_profiles
from modules.ollama_manager import is_ollama_available, get_ollama_models
from modules.dynamic_query_engine import analyze_query_requirements

def serialize_datetime(obj):
    """JSON serializer for datetime objects"""
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def check_prerequisites():
    """Check if all prerequisites are met"""
    print("🔍 Checking prerequisites...")
    
    # Check AWS CLI
    aws_available = check_aws_cli_available()
    print(f"   AWS CLI: {'✅ Available' if aws_available else '❌ Not configured'}")
    
    if aws_available:
        profiles = get_aws_profiles()
        print(f"   AWS Profiles: {', '.join(profiles) if profiles else 'None'}")
    
    # Check Ollama
    ollama_available = is_ollama_available()
    print(f"   Ollama: {'✅ Available' if ollama_available else '❌ Not running'}")
    
    if ollama_available:
        models = get_ollama_models()
        print(f"   Ollama Models: {', '.join(models) if models else 'None'}")
    
    return aws_available

def demo_aws_data_collection():
    """Demonstrate AWS data collection"""
    print("\n📊 Demo: AWS Data Collection")
    print("=" * 50)
    
    # Show available services
    services = get_aws_services_list()
    print(f"Available services: {', '.join(services[:5])}... (showing first 5)")
    
    # Collect data from a few services
    demo_services = ['ec2', 'rds', 's3']
    print(f"\nCollecting data from: {', '.join(demo_services)}")
    
    try:
        data = collect_aws_data(demo_services, 'default')
        
        print("\n✅ Data collected successfully!")
        for service, service_data in data.items():
            if service_data:
                count = len(service_data) if isinstance(service_data, list) else len(service_data.keys())
                print(f"   {service}: {count} resources")
            else:
                print(f"   {service}: No resources found")
                
    except Exception as e:
        print(f"❌ Error collecting data: {str(e)}")
        return None
    
    return data

def demo_query_analysis():
    """Demonstrate query analysis"""
    print("\n🧠 Demo: Query Analysis")
    print("=" * 50)
    
    sample_queries = [
        "Show me all running EC2 instances",
        "What RDS databases do I have?",
        "Which security groups allow access from anywhere?",
        "List my S3 buckets with public access"
    ]
    
    for query in sample_queries:
        print(f"\nAnalyzing: '{query}'")
        try:
            analysis = analyze_query_requirements(query)
            services = analysis.get('services', [])
            intent = analysis.get('intent', 'Unknown')
            print(f"   Intent: {intent}")
            print(f"   Services needed: {', '.join(services)}")
        except Exception as e:
            print(f"   Error: {str(e)}")

def demo_data_export():
    """Demonstrate data export functionality"""
    print("\n📁 Demo: Data Export")
    print("=" * 50)
    
    # Create sample data
    sample_data = {
        "ec2": [
            {
                "InstanceId": "i-1234567890abcdef0",
                "InstanceType": "t3.medium",
                "State": {"Name": "running"},
                "PublicIpAddress": "52.1.2.3",
                "Tags": [{"Key": "Name", "Value": "web-server"}]
            }
        ],
        "rds": [
            {
                "DBInstanceIdentifier": "mydb",
                "DBInstanceClass": "db.t3.micro",
                "Engine": "mysql",
                "DBInstanceStatus": "available"
            }
        ]
    }
    
    # Export to JSON
    try:
        json_output = json.dumps(sample_data, default=serialize_datetime, indent=2)
        print("✅ JSON export successful")
        print(f"   Size: {len(json_output)} characters")
        
        # Show first few lines
        lines = json_output.split('\n')[:5]
        for line in lines:
            print(f"   {line}")
        print("   ...")
        
    except Exception as e:
        print(f"❌ Export error: {str(e)}")

def main():
    """Main demo function"""
    print("🧠 AWS Infrastructure Explainer - Demo")
    print("=" * 60)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please configure AWS CLI first.")
        print("   Run: aws configure")
        return
    
    # Demo AWS data collection
    data = demo_aws_data_collection()
    
    # Demo query analysis
    demo_query_analysis()
    
    # Demo data export
    demo_data_export()
    
    print("\n🎉 Demo completed!")
    print("\nNext steps:")
    print("1. Run the full application: streamlit run ui-app-new.py")
    print("2. Configure your LLM provider (Ollama or Bedrock)")
    print("3. Try the Smart Query engine with your own questions")
    print("4. Explore Complex Queries and Resource Interaction features")

if __name__ == "__main__":
    main()
