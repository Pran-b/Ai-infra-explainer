import boto3
import json
import streamlit as st
from botocore.exceptions import ClientError
from typing import Dict, List, Any, Optional
from datetime import datetime
import copy


def serialize_datetime(obj):
    """Convert datetime objects to string for JSON serialization"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: serialize_datetime(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_datetime(item) for item in obj]
    else:
        return obj


class DynamicAWSQueryEngine:
    """Engine that fetches AWS data dynamically based on query requirements"""
    
    def __init__(self):
        self.query_to_services = {
            'ec2': ['EC2'],
            'instance': ['EC2'],
            'security group': ['EC2'],
            'vpc': ['EC2'],
            'subnet': ['EC2'],
            'volume': ['EC2'],
            's3': ['S3'],
            'bucket': ['S3'],
            'lambda': ['Lambda'],
            'function': ['Lambda'],
            'iam': ['IAM'],
            'user': ['IAM'],
            'role': ['IAM'],
            'policy': ['IAM'],
            'rds': ['RDS'],
            'database': ['RDS'],
            'dynamodb': ['DynamoDB'],
            'table': ['DynamoDB'],
            'cloudformation': ['CloudFormation'],
            'stack': ['CloudFormation'],
            'ecs': ['ECS'],
            'cluster': ['ECS'],
            'service': ['ECS'],
            'eks': ['EKS'],
            'api gateway': ['API Gateway'],
            'cloudwatch': ['CloudWatch'],
            'alarm': ['CloudWatch'],
            'log group': ['CloudWatch']
        }
        
        self.service_collectors = {
            'EC2': self._collect_ec2_data,
            'S3': self._collect_s3_data,
            'Lambda': self._collect_lambda_data,
            'IAM': self._collect_iam_data,
            'RDS': self._collect_rds_data,
            'DynamoDB': self._collect_dynamodb_data,
            'CloudFormation': self._collect_cloudformation_data,
            'ECS': self._collect_ecs_data,
            'EKS': self._collect_eks_data,
            'API Gateway': self._collect_apigateway_data,
            'CloudWatch': self._collect_cloudwatch_data
        }
    
    def analyze_query_requirements(self, query: str) -> List[str]:
        """Analyze query to determine which AWS services are needed"""
        query_lower = query.lower()
        required_services = set()
        
        # Check for service keywords in query
        for keyword, services in self.query_to_services.items():
            if keyword in query_lower:
                required_services.update(services)
        
        # If no specific services detected, default to core services
        if not required_services:
            required_services = {'EC2', 'S3', 'Lambda'}
        
        return list(required_services)
    
    def collect_targeted_data(self, query: str, aws_profile: str = None) -> Dict[str, Any]:
        """Collect only the AWS data needed for the specific query"""
        required_services = self.analyze_query_requirements(query)
        
        st.info(f"🎯 **Smart Data Collection**: Only fetching {', '.join(required_services)} data for your query")
        
        collected_data = {}
        progress_bar = st.progress(0)
        
        for i, service in enumerate(required_services):
            try:
                progress_bar.progress((i + 1) / len(required_services))
                st.text(f"Collecting {service} data...")
                
                if service in self.service_collectors:
                    collector = self.service_collectors[service]
                    service_data = collector(aws_profile)
                    collected_data.update(service_data)
                else:
                    st.warning(f"No collector available for {service}")
                    
            except Exception as e:
                st.error(f"Error collecting {service} data: {str(e)}")
                collected_data[service] = {'error': str(e)}
        
        progress_bar.empty()
        st.success(f"✅ Successfully collected data for {len(required_services)} services")
        
        return collected_data
    
    def _get_boto3_client(self, service_name: str, aws_profile: str = None):
        """Get boto3 client with optional profile"""
        if aws_profile and aws_profile != "default":
            session = boto3.Session(profile_name=aws_profile)
            return session.client(service_name.lower())
        else:
            return boto3.client(service_name.lower())
    
    def _collect_ec2_data(self, aws_profile: str = None) -> Dict[str, Any]:
        """Collect EC2 data efficiently"""
        ec2 = self._get_boto3_client('ec2', aws_profile)
        data = {}
        
        try:
            # Only collect the most commonly queried EC2 resources
            data['instances'] = ec2.describe_instances().get('Reservations', [])
            data['security_groups'] = ec2.describe_security_groups().get('SecurityGroups', [])
            data['vpcs'] = ec2.describe_vpcs().get('Vpcs', [])
            data['subnets'] = ec2.describe_subnets().get('Subnets', [])
            
            # Serialize datetime objects
            data = serialize_datetime(data)
            
            # Optional: only collect if needed
            # data['volumes'] = ec2.describe_volumes().get('Volumes', [])
            # data['route_tables'] = ec2.describe_route_tables().get('RouteTables', [])
            
        except ClientError as e:
            data['error'] = str(e)
        
        return {"EC2": data}
    
    def _collect_s3_data(self, aws_profile: str = None) -> Dict[str, Any]:
        """Collect S3 data efficiently"""
        s3 = self._get_boto3_client('s3', aws_profile)
        data = {}
        
        try:
            buckets = s3.list_buckets().get('Buckets', [])
            data['buckets'] = buckets
            
            # Optionally collect bucket details for first few buckets
            if buckets and len(buckets) <= 10:  # Only for small number of buckets
                for bucket in buckets[:5]:  # Limit to first 5 buckets
                    bucket_name = bucket['Name']
                    try:
                        # Get bucket location
                        location = s3.get_bucket_location(Bucket=bucket_name)
                        bucket['Region'] = location.get('LocationConstraint', 'us-east-1')
                        
                        # Get bucket policy (if exists)
                        try:
                            policy = s3.get_bucket_policy(Bucket=bucket_name)
                            bucket['Policy'] = json.loads(policy['Policy'])
                        except ClientError:
                            bucket['Policy'] = None
                            
                    except ClientError:
                        continue
            
        except ClientError as e:
            data['error'] = str(e)
        
        # Serialize datetime objects
        data = serialize_datetime(data)
        
        return {"S3": data}
    
    def _collect_lambda_data(self, aws_profile: str = None) -> Dict[str, Any]:
        """Collect Lambda data efficiently"""
        lambda_client = self._get_boto3_client('lambda', aws_profile)
        data = {}
        
        try:
            functions = lambda_client.list_functions().get('Functions', [])
            data['functions'] = functions
            
            # Optionally get function details for first few functions
            if functions and len(functions) <= 20:  # Only for reasonable number of functions
                for func in functions[:10]:  # Limit to first 10 functions
                    func_name = func['FunctionName']
                    try:
                        # Get function configuration
                        config = lambda_client.get_function_configuration(FunctionName=func_name)
                        func['DetailedConfig'] = config
                    except ClientError:
                        continue
            
        except ClientError as e:
            data['error'] = str(e)
        
        # Serialize datetime objects
        data = serialize_datetime(data)
        
        return {"Lambda": data}
    
    def _collect_iam_data(self, aws_profile: str = None) -> Dict[str, Any]:
        """Collect IAM data efficiently"""
        iam = self._get_boto3_client('iam', aws_profile)
        data = {}
        
        try:
            # Collect basic IAM resources
            data['users'] = iam.list_users().get('Users', [])
            data['roles'] = iam.list_roles().get('Roles', [])
            data['groups'] = iam.list_groups().get('Groups', [])
            data['policies'] = iam.list_policies(Scope='Local').get('Policies', [])
            
        except ClientError as e:
            data['error'] = str(e)
        
        # Serialize datetime objects
        data = serialize_datetime(data)
        
        return {"IAM": data}
    
    def _collect_rds_data(self, aws_profile: str = None) -> Dict[str, Any]:
        """Collect RDS data efficiently"""
        rds = self._get_boto3_client('rds', aws_profile)
        data = {}
        
        try:
            data['db_instances'] = rds.describe_db_instances().get('DBInstances', [])
            data['db_clusters'] = rds.describe_db_clusters().get('DBClusters', [])
            
        except ClientError as e:
            data['error'] = str(e)
        
        # Serialize datetime objects
        data = serialize_datetime(data)
        
        return {"RDS": data}
    
    def _collect_dynamodb_data(self, aws_profile: str = None) -> Dict[str, Any]:
        """Collect DynamoDB data efficiently"""
        dynamodb = self._get_boto3_client('dynamodb', aws_profile)
        data = {}
        
        try:
            table_names = dynamodb.list_tables().get('TableNames', [])
            data['tables'] = []
            
            # Get table details for first few tables
            for table_name in table_names[:10]:  # Limit to first 10 tables
                try:
                    table_info = dynamodb.describe_table(TableName=table_name)
                    data['tables'].append(table_info['Table'])
                except ClientError:
                    continue
            
        except ClientError as e:
            data['error'] = str(e)
        
        # Serialize datetime objects
        data = serialize_datetime(data)
        
        return {"DynamoDB": data}
    
    def _collect_cloudformation_data(self, aws_profile: str = None) -> Dict[str, Any]:
        """Collect CloudFormation data efficiently"""
        cf = self._get_boto3_client('cloudformation', aws_profile)
        data = {}
        
        try:
            stacks = cf.list_stacks(StackStatusFilter=[
                'CREATE_COMPLETE', 'UPDATE_COMPLETE', 'ROLLBACK_COMPLETE'
            ]).get('StackSummaries', [])
            data['stacks'] = stacks
            
        except ClientError as e:
            data['error'] = str(e)
        
        # Serialize datetime objects
        data = serialize_datetime(data)
        
        return {"CloudFormation": data}
    
    def _collect_ecs_data(self, aws_profile: str = None) -> Dict[str, Any]:
        """Collect ECS data efficiently"""
        ecs = self._get_boto3_client('ecs', aws_profile)
        data = {}
        
        try:
            cluster_arns = ecs.list_clusters().get('clusterArns', [])
            data['clusters'] = []
            
            for cluster_arn in cluster_arns:
                try:
                    cluster_info = ecs.describe_clusters(clusters=[cluster_arn])
                    data['clusters'].extend(cluster_info['clusters'])
                except ClientError:
                    continue
            
        except ClientError as e:
            data['error'] = str(e)
        
        # Serialize datetime objects
        data = serialize_datetime(data)
        
        return {"ECS": data}
    
    def _collect_eks_data(self, aws_profile: str = None) -> Dict[str, Any]:
        """Collect EKS data efficiently"""
        eks = self._get_boto3_client('eks', aws_profile)
        data = {}
        
        try:
            cluster_names = eks.list_clusters().get('clusters', [])
            data['clusters'] = []
            
            for cluster_name in cluster_names:
                try:
                    cluster_info = eks.describe_cluster(name=cluster_name)
                    data['clusters'].append(cluster_info['cluster'])
                except ClientError:
                    continue
            
        except ClientError as e:
            data['error'] = str(e)
        
        # Serialize datetime objects
        data = serialize_datetime(data)
        
        return {"EKS": data}
    
    def _collect_apigateway_data(self, aws_profile: str = None) -> Dict[str, Any]:
        """Collect API Gateway data efficiently"""
        apigw = self._get_boto3_client('apigateway', aws_profile)
        data = {}
        
        try:
            apis = apigw.get_rest_apis().get('items', [])
            data['apis'] = apis
            
        except ClientError as e:
            data['error'] = str(e)
        
        # Serialize datetime objects
        data = serialize_datetime(data)
        
        return {"API Gateway": data}
    
    def _collect_cloudwatch_data(self, aws_profile: str = None) -> Dict[str, Any]:
        """Collect CloudWatch data efficiently"""
        cloudwatch = self._get_boto3_client('cloudwatch', aws_profile)
        logs = self._get_boto3_client('logs', aws_profile)
        data = {}
        
        try:
            # Get alarms
            data['alarms'] = cloudwatch.describe_alarms().get('MetricAlarms', [])
            
            # Get log groups (limited)
            data['log_groups'] = logs.describe_log_groups(limit=20).get('logGroups', [])
            
        except ClientError as e:
            data['error'] = str(e)
        
        # Serialize datetime objects
        data = serialize_datetime(data)
        
        return {"CloudWatch": data}
    
    def get_query_suggestions(self, partial_query: str) -> List[str]:
        """Get query suggestions based on partial input"""
        suggestions = []
        partial_lower = partial_query.lower()
        
        # Common query patterns
        query_patterns = [
            "Show me running EC2 instances",
            "List all S3 buckets",
            "What Lambda functions do I have?",
            "Show security groups with open ports",
            "List IAM users and their roles",
            "Show RDS databases",
            "List DynamoDB tables",
            "Show CloudFormation stacks",
            "What ECS clusters exist?",
            "Show API Gateway endpoints",
            "List CloudWatch alarms",
            "Show unused resources",
            "Find expensive resources",
            "Security compliance check",
            "Show VPC resources",
            "List EC2 instances with public IPs"
        ]
        
        # Filter suggestions based on partial query
        for pattern in query_patterns:
            if any(word in pattern.lower() for word in partial_lower.split()):
                suggestions.append(pattern)
        
        return suggestions[:5]  # Return top 5 suggestions


# Global instance
dynamic_query_engine = DynamicAWSQueryEngine()
