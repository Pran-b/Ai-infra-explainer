import boto3
import json
from botocore.exceptions import ClientError

def get_iam_info():
    iam = boto3.client('iam')
    data = {}
    try:
        data['users'] = iam.list_users().get('Users', [])
        data['roles'] = iam.list_roles().get('Roles', [])
        data['policies'] = iam.list_policies(Scope='Local').get('Policies', [])
        data['groups'] = iam.list_groups().get('Groups', [])
        data['instance_profiles'] = iam.list_instance_profiles().get('InstanceProfiles', [])
    except ClientError as e:
        data['error'] = str(e)
    return {"IAM": data}

def get_ec2_info():
    ec2 = boto3.client('ec2')
    data = {}
    try:
        data['instances'] = ec2.describe_instances().get('Reservations', [])
        data['security_groups'] = ec2.describe_security_groups().get('SecurityGroups', [])
        data['volumes'] = ec2.describe_volumes().get('Volumes', [])
        data['vpcs'] = ec2.describe_vpcs().get('Vpcs', [])
        data['subnets'] = ec2.describe_subnets().get('Subnets', [])
        data['route_tables'] = ec2.describe_route_tables().get('RouteTables', [])
        data['network_acls'] = ec2.describe_network_acls().get('NetworkAcls', [])
        data['availability_zones'] = ec2.describe_availability_zones().get('AvailabilityZones', [])
    except ClientError as e:
        data['error'] = str(e)
    return {"EC2": data}

def get_s3_info():
    s3 = boto3.client('s3')
    data = {}
    try:
        data['buckets'] = s3.list_buckets().get('Buckets', [])
    except ClientError as e:
        data['error'] = str(e)
    return {"S3": data}

def get_lambda_info():
    lam = boto3.client('lambda')
    data = {}
    try:
        data['functions'] = lam.list_functions().get('Functions', [])
    except ClientError as e:
        data['error'] = str(e)
    return {"Lambda": data}

def get_elb_info():
    elb = boto3.client('elbv2')
    data = {}
    try:
        data['load_balancers'] = elb.describe_load_balancers().get('LoadBalancers', [])
        data['target_groups'] = elb.describe_target_groups().get('TargetGroups', [])
    except ClientError as e:
        data['error'] = str(e)
    return {"ELB": data}

def get_eks_info():
    eks = boto3.client('eks')
    data = {}
    try:
        data['clusters'] = eks.list_clusters().get('clusters', [])
    except ClientError as e:
        data['error'] = str(e)
    return {"EKS": data}

def get_route53_info():
    r53 = boto3.client('route53')
    data = {}
    try:
        data['hosted_zones'] = r53.list_hosted_zones().get('HostedZones', [])
    except ClientError as e:
        data['error'] = str(e)
    return {"Route53": data}

def get_cloudformation_info():
    cf = boto3.client('cloudformation')
    data = {}
    try:
        data['stacks'] = cf.describe_stacks().get('Stacks', [])
    except ClientError as e:
        data['error'] = str(e)
    return {"CloudFormation": data}

def get_codebuild_info():
    cb = boto3.client('codebuild')
    data = {}
    try:
        data['projects'] = cb.list_projects().get('projects', [])
    except ClientError as e:
        data['error'] = str(e)
    return {"CodeBuild": data}

def get_codepipeline_info():
    cp = boto3.client('codepipeline')
    data = {}
    try:
        data['pipelines'] = cp.list_pipelines().get('pipelines', [])
    except ClientError as e:
        data['error'] = str(e)
    return {"CodePipeline": data}

def get_rds_info():
    rds = boto3.client('rds')
    data = {}
    try:
        data['instances'] = rds.describe_db_instances().get('DBInstances', [])
    except ClientError as e:
        data['error'] = str(e)
    return {"RDS": data}

def get_dynamodb_info():
    db = boto3.client('dynamodb')
    data = {}
    try:
        data['tables'] = db.list_tables().get('TableNames', [])
    except ClientError as e:
        data['error'] = str(e)
    return {"DynamoDB": data}

def get_billing_info():
    ce = boto3.client('ce')
    data = {}
    try:
        data['budgets'] = ce.get_cost_and_usage(
            TimePeriod={
                'Start': '2024-01-01',
                'End': '2024-12-31'
            },
            Granularity='MONTHLY',
            Metrics=['UnblendedCost']
        )
    except ClientError as e:
        data['error'] = str(e)
    return {"Billing": data}

def collect_selected_services(selected_services):
    service_map = {
        'IAM': get_iam_info,
        'EC2': get_ec2_info,
        'S3': get_s3_info,
        'Lambda': get_lambda_info,
        'ELB': get_elb_info,
        'EKS': get_eks_info,
        'Route53': get_route53_info,
        'CloudFormation': get_cloudformation_info,
        'CodeBuild': get_codebuild_info,
        'CodePipeline': get_codepipeline_info,
        'RDS': get_rds_info,
        'DynamoDB': get_dynamodb_info,
        'Billing': get_billing_info
    }
    aws_data = {}
    for service in selected_services:
        if service in service_map:
            aws_data.update(service_map[service]())
    return aws_data

def format_data_for_llm(aws_data):
    documents = []
    for service, content in aws_data.items():
        doc = f"AWS {service} Information:\n" + json.dumps(content, indent=2)
        documents.append(doc)
    return documents
