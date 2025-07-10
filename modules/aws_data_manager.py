import datetime
import json
import streamlit as st
from aws_collector import collect_selected_services


def serialize(obj):
    """Serialize datetime objects for JSON"""
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def collect_aws_data(selected_services):
    """Collect AWS data for selected services"""
    try:
        with st.spinner("Fetching data from AWS..."):
            aws_data = collect_selected_services(selected_services)
            aws_data = json.loads(json.dumps(aws_data, default=serialize))
            st.session_state["aws_raw_data"] = aws_data
        st.success("AWS data collected for: " + ", ".join(selected_services))
        return True
    except Exception as e:
        st.error(f"Error collecting AWS data: {str(e)}")
        return False


def get_aws_services_list():
    """Get the list of supported AWS services"""
    return [
        "EC2", "EKS", "RDS", "VPC", "Subnets", "Security Groups", "IAM",
        "Route53", "S3", "LoadBalancers", "CloudFormation", "CodeBuild",
        "CodePipeline", "Budgets", "Billing", "DynamoDB"
    ]


def get_default_services():
    """Get default AWS services for analysis"""
    return ["EC2", "RDS", "IAM"]
