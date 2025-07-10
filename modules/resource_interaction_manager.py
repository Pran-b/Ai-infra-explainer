import json
import streamlit as st
from typing import Dict, List, Any, Optional, Tuple
from modules.bedrock_query_engine import query_bedrock_model
from qa_engine import query_aws_knowledgebase


class ResourceInteractionManager:
    """Manager for individual resource interactions with AI"""
    
    def __init__(self):
        self.supported_resource_types = {
            'EC2': ['instances', 'security_groups', 'volumes', 'vpcs', 'subnets'],
            'S3': ['buckets'],
            'Lambda': ['functions'],
            'IAM': ['users', 'roles', 'policies', 'groups'],
            'RDS': ['db_instances', 'db_clusters'],
            'DynamoDB': ['tables'],
            'CloudFormation': ['stacks'],
            'ECS': ['clusters', 'services'],
            'EKS': ['clusters'],
            'API Gateway': ['apis', 'stages'],
            'CloudWatch': ['alarms', 'log_groups']
        }
    
    def extract_individual_resources(self, aws_data: Dict) -> Dict[str, List[Dict]]:
        """Extract individual resources from AWS data for interaction"""
        resources = {}
        
        for service, service_data in aws_data.items():
            if isinstance(service_data, dict) and 'error' not in service_data:
                resources[service] = {}
                
                for resource_type, resource_list in service_data.items():
                    if isinstance(resource_list, list) and resource_list:
                        resources[service][resource_type] = resource_list
        
        return resources
    
    def get_resource_summary(self, resource: Dict, resource_type: str) -> str:
        """Generate a concise summary of a resource"""
        summary_parts = []
        
        # Resource type specific summaries
        if resource_type == 'instances':
            instance_id = resource.get('InstanceId', 'Unknown')
            state = resource.get('State', {}).get('Name', 'Unknown')
            instance_type = resource.get('InstanceType', 'Unknown')
            summary_parts.append(f"EC2 Instance: {instance_id} ({instance_type}) - {state}")
            
        elif resource_type == 'security_groups':
            group_id = resource.get('GroupId', 'Unknown')
            group_name = resource.get('GroupName', 'Unknown')
            vpc_id = resource.get('VpcId', 'Unknown')
            summary_parts.append(f"Security Group: {group_name} ({group_id}) in VPC {vpc_id}")
            
        elif resource_type == 'buckets':
            bucket_name = resource.get('Name', 'Unknown')
            creation_date = resource.get('CreationDate', 'Unknown')
            summary_parts.append(f"S3 Bucket: {bucket_name} (created: {creation_date})")
            
        elif resource_type == 'functions':
            function_name = resource.get('FunctionName', 'Unknown')
            runtime = resource.get('Runtime', 'Unknown')
            memory = resource.get('MemorySize', 'Unknown')
            summary_parts.append(f"Lambda Function: {function_name} ({runtime}) - {memory}MB")
            
        elif resource_type == 'volumes':
            volume_id = resource.get('VolumeId', 'Unknown')
            size = resource.get('Size', 'Unknown')
            volume_type = resource.get('VolumeType', 'Unknown')
            state = resource.get('State', 'Unknown')
            summary_parts.append(f"EBS Volume: {volume_id} ({volume_type}) - {size}GB - {state}")
            
        elif resource_type == 'vpcs':
            vpc_id = resource.get('VpcId', 'Unknown')
            cidr = resource.get('CidrBlock', 'Unknown')
            state = resource.get('State', 'Unknown')
            summary_parts.append(f"VPC: {vpc_id} ({cidr}) - {state}")
            
        elif resource_type == 'users':
            username = resource.get('UserName', 'Unknown')
            created = resource.get('CreateDate', 'Unknown')
            summary_parts.append(f"IAM User: {username} (created: {created})")
            
        elif resource_type == 'roles':
            role_name = resource.get('RoleName', 'Unknown')
            created = resource.get('CreateDate', 'Unknown')
            summary_parts.append(f"IAM Role: {role_name} (created: {created})")
            
        else:
            # Generic summary for unknown resource types
            if 'Name' in resource:
                summary_parts.append(f"{resource_type}: {resource['Name']}")
            elif 'Id' in resource:
                summary_parts.append(f"{resource_type}: {resource['Id']}")
            else:
                summary_parts.append(f"{resource_type}: Resource")
        
        return ' | '.join(summary_parts) if summary_parts else f"{resource_type}: Resource"
    
    def format_resource_for_ai(self, resource: Dict, resource_type: str, service: str) -> str:
        """Format a single resource for AI interaction"""
        formatted_parts = [
            f"=== {service} {resource_type.title()} ===",
            json.dumps(resource, indent=2, default=str)
        ]
        return '\n'.join(formatted_parts)
    
    def create_resource_context(self, selected_resources: List[Tuple[str, str, int]], aws_data: Dict) -> str:
        """Create context from selected resources for AI interaction"""
        context_parts = []
        resources = self.extract_individual_resources(aws_data)
        
        for service, resource_type, resource_index in selected_resources:
            if (service in resources and 
                resource_type in resources[service] and 
                resource_index < len(resources[service][resource_type])):
                
                resource = resources[service][resource_type][resource_index]
                formatted_resource = self.format_resource_for_ai(resource, resource_type, service)
                context_parts.append(formatted_resource)
        
        return '\n\n'.join(context_parts)
    
    def query_resources(self, query: str, selected_resources: List[Tuple[str, str, int]], 
                       aws_data: Dict, llm_provider: str, model_config: Dict) -> Optional[str]:
        """Query AI about specific resources"""
        
        # Create context from selected resources
        context = self.create_resource_context(selected_resources, aws_data)
        
        if not context:
            return "No valid resources selected for querying."
        
        # Create a focused prompt for resource interaction
        focused_prompt = f"""You are an AWS infrastructure expert. I'm asking about specific AWS resources.

Selected AWS Resources:
{context}

Question: {query}

Please provide detailed information about these specific resources, including:
- Current configuration and status
- Security implications
- Cost optimization suggestions
- Best practices recommendations
- Potential issues or risks

Focus your response on the selected resources only."""
        
        try:
            if llm_provider == "Ollama":
                response = query_aws_knowledgebase(
                    focused_prompt,
                    [context],
                    embed_model='nomic-embed-text',
                    llm_model=model_config.get('model_name')
                )
            elif llm_provider == "Bedrock":
                response = query_bedrock_model(
                    query=focused_prompt,
                    text_documents=[context],
                    model_id=model_config.get('model_id'),
                    aws_region=model_config.get('aws_region'),
                    aws_access_key=model_config.get('aws_access_key'),
                    aws_secret_key=model_config.get('aws_secret_key'),
                    use_cli_creds=model_config.get('use_cli_creds', False),
                    debug=model_config.get('debug', False),
                    aws_profile=model_config.get('aws_profile')
                )
            else:
                return "Unsupported LLM provider"
            
            return response
            
        except Exception as e:
            return f"Error querying resources: {str(e)}"
    
    def get_resource_actions(self, resource_type: str) -> List[str]:
        """Get suggested actions for a resource type"""
        actions = {
            'instances': [
                'Analyze security configuration',
                'Check cost optimization opportunities',
                'Review performance metrics',
                'Evaluate backup strategy',
                'Assess compliance status'
            ],
            'security_groups': [
                'Audit inbound/outbound rules',
                'Check for overly permissive rules',
                'Review unused security groups',
                'Analyze traffic patterns',
                'Compliance verification'
            ],
            'buckets': [
                'Review access policies',
                'Check encryption settings',
                'Analyze storage costs',
                'Verify versioning configuration',
                'Security audit'
            ],
            'functions': [
                'Performance optimization',
                'Cost analysis',
                'Security review',
                'Runtime updates',
                'Memory optimization'
            ],
            'volumes': [
                'Performance analysis',
                'Cost optimization',
                'Backup verification',
                'Encryption status',
                'Usage patterns'
            ]
        }
        
        return actions.get(resource_type, [
            'Configuration review',
            'Security analysis',
            'Cost optimization',
            'Performance check',
            'Compliance audit'
        ])
    
    def create_resource_recommendations(self, resource: Dict, resource_type: str) -> List[str]:
        """Generate AI-powered recommendations for a resource"""
        recommendations = []
        
        # Basic recommendations based on resource type and configuration
        if resource_type == 'instances':
            state = resource.get('State', {}).get('Name', '')
            if state == 'running':
                recommendations.append("✅ Instance is running")
            elif state == 'stopped':
                recommendations.append("⚠️ Instance is stopped - consider terminating if not needed")
            
            # Check for public IP
            if resource.get('PublicIpAddress'):
                recommendations.append("🔒 Instance has public IP - review security groups")
        
        elif resource_type == 'security_groups':
            rules = resource.get('IpPermissions', [])
            for rule in rules:
                for ip_range in rule.get('IpRanges', []):
                    if ip_range.get('CidrIp') == '0.0.0.0/0':
                        recommendations.append("🚨 Security group allows access from anywhere (0.0.0.0/0)")
        
        elif resource_type == 'buckets':
            recommendations.append("🔍 Check bucket policies and ACLs")
            recommendations.append("🔒 Verify encryption settings")
        
        elif resource_type == 'functions':
            memory = resource.get('MemorySize', 0)
            if memory > 1024:
                recommendations.append(f"💰 High memory allocation ({memory}MB) - consider optimization")
            
            if resource.get('Runtime', '').startswith('python2'):
                recommendations.append("⚠️ Using deprecated Python 2 runtime")
        
        return recommendations if recommendations else ["ℹ️ No specific recommendations available"]
    
    def compare_resources(self, resource1: Dict, resource2: Dict, resource_type: str) -> str:
        """Compare two resources of the same type"""
        comparison_parts = [
            f"=== Comparing {resource_type.title()} ===",
            "",
            "Resource 1:",
            json.dumps(resource1, indent=2, default=str),
            "",
            "Resource 2:",
            json.dumps(resource2, indent=2, default=str),
            "",
            "Please analyze the differences between these resources and provide recommendations."
        ]
        return '\n'.join(comparison_parts)
    
    def get_resource_relationships(self, resource: Dict, resource_type: str, all_resources: Dict) -> List[str]:
        """Find relationships between resources"""
        relationships = []
        
        if resource_type == 'instances':
            instance_id = resource.get('InstanceId')
            vpc_id = resource.get('VpcId')
            subnet_id = resource.get('SubnetId')
            
            # Find related security groups
            for sg in resource.get('SecurityGroups', []):
                relationships.append(f"Uses Security Group: {sg.get('GroupName')} ({sg.get('GroupId')})")
            
            # Find related VPC
            if vpc_id:
                relationships.append(f"Located in VPC: {vpc_id}")
            
            # Find related subnet
            if subnet_id:
                relationships.append(f"Located in Subnet: {subnet_id}")
        
        elif resource_type == 'security_groups':
            group_id = resource.get('GroupId')
            vpc_id = resource.get('VpcId')
            
            if vpc_id:
                relationships.append(f"Belongs to VPC: {vpc_id}")
            
            # Find instances using this security group
            for service, service_resources in all_resources.items():
                if service == 'EC2' and 'instances' in service_resources:
                    for reservation in service_resources['instances']:
                        for instance in reservation.get('Instances', []):
                            for sg in instance.get('SecurityGroups', []):
                                if sg.get('GroupId') == group_id:
                                    instance_id = instance.get('InstanceId')
                                    relationships.append(f"Used by Instance: {instance_id}")
        
        return relationships


# Global instance
resource_manager = ResourceInteractionManager()
