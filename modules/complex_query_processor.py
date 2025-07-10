import json
import re
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict
import pandas as pd
import streamlit as st


class ComplexQueryProcessor:
    """Processor for handling complex structured queries about AWS infrastructure"""
    
    def __init__(self):
        self.query_patterns = {
            'ec2_with_security_groups': {
                'pattern': r'(running\s+ec2|ec2.*running).*security\s+group',
                'processor': self._process_ec2_with_security_groups
            },
            'security_group_usage': {
                'pattern': r'security\s+group.*usage|which.*security\s+group',
                'processor': self._process_security_group_usage
            },
            'vpc_resources': {
                'pattern': r'vpc.*resource|resource.*vpc',
                'processor': self._process_vpc_resources
            },
            'instance_details': {
                'pattern': r'instance.*detail|detail.*instance',
                'processor': self._process_instance_details
            },
            'cost_analysis': {
                'pattern': r'cost|expensive|cheap|price',
                'processor': self._process_cost_analysis
            },
            'compliance_check': {
                'pattern': r'compliance|compliant|standard|policy',
                'processor': self._process_compliance_check
            },
            'resource_relationships': {
                'pattern': r'relationship|connect|depend|link',
                'processor': self._process_resource_relationships
            },
            'unused_resources': {
                'pattern': r'unused|idle|orphan|waste',
                'processor': self._process_unused_resources
            }
        }
    
    def detect_query_type(self, query: str) -> Optional[str]:
        """Detect the type of complex query based on patterns"""
        query_lower = query.lower()
        
        for query_type, config in self.query_patterns.items():
            if re.search(config['pattern'], query_lower):
                return query_type
        
        return None
    
    def process_complex_query(self, query: str, aws_data: Dict) -> Dict[str, Any]:
        """Process a complex query and return structured results"""
        query_type = self.detect_query_type(query)
        
        if query_type and query_type in self.query_patterns:
            processor = self.query_patterns[query_type]['processor']
            return processor(query, aws_data)
        
        return {'type': 'general', 'data': None, 'message': 'Query not recognized as complex structured query'}
    
    def _process_ec2_with_security_groups(self, query: str, aws_data: Dict) -> Dict[str, Any]:
        """Process queries about EC2 instances and their security groups"""
        results = []
        unique_security_groups = set()
        
        if 'EC2' in aws_data and 'instances' in aws_data['EC2']:
            for reservation in aws_data['EC2']['instances']:
                for instance in reservation.get('Instances', []):
                    instance_id = instance.get('InstanceId', 'Unknown')
                    instance_type = instance.get('InstanceType', 'Unknown')
                    state = instance.get('State', {}).get('Name', 'Unknown')
                    
                    # Filter for running instances if specified
                    if 'running' in query.lower() and state != 'running':
                        continue
                    
                    # Extract security groups
                    security_groups = []
                    for sg in instance.get('SecurityGroups', []):
                        sg_id = sg.get('GroupId', 'Unknown')
                        sg_name = sg.get('GroupName', 'Unknown')
                        security_groups.append({'id': sg_id, 'name': sg_name})
                        unique_security_groups.add(f"{sg_name} ({sg_id})")
                    
                    results.append({
                        'instance_id': instance_id,
                        'instance_type': instance_type,
                        'state': state,
                        'security_groups': security_groups,
                        'public_ip': instance.get('PublicIpAddress', 'None'),
                        'private_ip': instance.get('PrivateIpAddress', 'None'),
                        'vpc_id': instance.get('VpcId', 'Unknown'),
                        'subnet_id': instance.get('SubnetId', 'Unknown')
                    })
        
        return {
            'type': 'ec2_with_security_groups',
            'data': results,
            'unique_security_groups': sorted(list(unique_security_groups)),
            'summary': {
                'total_instances': len(results),
                'unique_security_groups_count': len(unique_security_groups)
            }
        }
    
    def _process_security_group_usage(self, query: str, aws_data: Dict) -> Dict[str, Any]:
        """Process queries about security group usage"""
        security_group_usage = defaultdict(list)
        unused_security_groups = []
        
        # Get all security groups
        all_security_groups = {}
        if 'EC2' in aws_data and 'security_groups' in aws_data['EC2']:
            for sg in aws_data['EC2']['security_groups']:
                sg_id = sg.get('GroupId', 'Unknown')
                all_security_groups[sg_id] = {
                    'id': sg_id,
                    'name': sg.get('GroupName', 'Unknown'),
                    'description': sg.get('Description', 'No description'),
                    'vpc_id': sg.get('VpcId', 'Unknown'),
                    'rules_count': len(sg.get('IpPermissions', []))
                }
        
        # Check usage by EC2 instances
        if 'EC2' in aws_data and 'instances' in aws_data['EC2']:
            for reservation in aws_data['EC2']['instances']:
                for instance in reservation.get('Instances', []):
                    instance_id = instance.get('InstanceId', 'Unknown')
                    instance_type = instance.get('InstanceType', 'Unknown')
                    state = instance.get('State', {}).get('Name', 'Unknown')
                    
                    for sg in instance.get('SecurityGroups', []):
                        sg_id = sg.get('GroupId', 'Unknown')
                        security_group_usage[sg_id].append({
                            'resource_type': 'EC2 Instance',
                            'resource_id': instance_id,
                            'resource_details': f"{instance_type} ({state})"
                        })
        
        # Find unused security groups
        for sg_id, sg_info in all_security_groups.items():
            if sg_id not in security_group_usage:
                unused_security_groups.append(sg_info)
        
        return {
            'type': 'security_group_usage',
            'data': {
                'usage_map': dict(security_group_usage),
                'all_security_groups': all_security_groups,
                'unused_security_groups': unused_security_groups
            },
            'summary': {
                'total_security_groups': len(all_security_groups),
                'used_security_groups': len(security_group_usage),
                'unused_security_groups': len(unused_security_groups)
            }
        }
    
    def _process_vpc_resources(self, query: str, aws_data: Dict) -> Dict[str, Any]:
        """Process queries about VPC resources"""
        vpc_resources = defaultdict(lambda: defaultdict(list))
        
        if 'EC2' in aws_data:
            # Process VPCs
            if 'vpcs' in aws_data['EC2']:
                for vpc in aws_data['EC2']['vpcs']:
                    vpc_id = vpc.get('VpcId', 'Unknown')
                    vpc_resources[vpc_id]['vpc_info'] = {
                        'cidr_block': vpc.get('CidrBlock', 'Unknown'),
                        'state': vpc.get('State', 'Unknown'),
                        'is_default': vpc.get('IsDefault', False)
                    }
            
            # Process instances in VPCs
            if 'instances' in aws_data['EC2']:
                for reservation in aws_data['EC2']['instances']:
                    for instance in reservation.get('Instances', []):
                        vpc_id = instance.get('VpcId', 'Unknown')
                        vpc_resources[vpc_id]['instances'].append({
                            'instance_id': instance.get('InstanceId', 'Unknown'),
                            'instance_type': instance.get('InstanceType', 'Unknown'),
                            'state': instance.get('State', {}).get('Name', 'Unknown'),
                            'subnet_id': instance.get('SubnetId', 'Unknown')
                        })
            
            # Process subnets in VPCs
            if 'subnets' in aws_data['EC2']:
                for subnet in aws_data['EC2']['subnets']:
                    vpc_id = subnet.get('VpcId', 'Unknown')
                    vpc_resources[vpc_id]['subnets'].append({
                        'subnet_id': subnet.get('SubnetId', 'Unknown'),
                        'cidr_block': subnet.get('CidrBlock', 'Unknown'),
                        'availability_zone': subnet.get('AvailabilityZone', 'Unknown'),
                        'available_ip_count': subnet.get('AvailableIpAddressCount', 0)
                    })
            
            # Process security groups in VPCs
            if 'security_groups' in aws_data['EC2']:
                for sg in aws_data['EC2']['security_groups']:
                    vpc_id = sg.get('VpcId', 'Unknown')
                    vpc_resources[vpc_id]['security_groups'].append({
                        'group_id': sg.get('GroupId', 'Unknown'),
                        'group_name': sg.get('GroupName', 'Unknown'),
                        'description': sg.get('Description', 'No description')
                    })
        
        return {
            'type': 'vpc_resources',
            'data': dict(vpc_resources),
            'summary': {
                'total_vpcs': len(vpc_resources),
                'total_instances': sum(len(vpc.get('instances', [])) for vpc in vpc_resources.values()),
                'total_subnets': sum(len(vpc.get('subnets', [])) for vpc in vpc_resources.values())
            }
        }
    
    def _process_instance_details(self, query: str, aws_data: Dict) -> Dict[str, Any]:
        """Process queries about instance details"""
        instance_details = []
        
        if 'EC2' in aws_data and 'instances' in aws_data['EC2']:
            for reservation in aws_data['EC2']['instances']:
                for instance in reservation.get('Instances', []):
                    details = {
                        'instance_id': instance.get('InstanceId', 'Unknown'),
                        'instance_type': instance.get('InstanceType', 'Unknown'),
                        'state': instance.get('State', {}).get('Name', 'Unknown'),
                        'launch_time': str(instance.get('LaunchTime', 'Unknown')),
                        'public_ip': instance.get('PublicIpAddress', 'None'),
                        'private_ip': instance.get('PrivateIpAddress', 'None'),
                        'vpc_id': instance.get('VpcId', 'Unknown'),
                        'subnet_id': instance.get('SubnetId', 'Unknown'),
                        'availability_zone': instance.get('Placement', {}).get('AvailabilityZone', 'Unknown'),
                        'key_name': instance.get('KeyName', 'None'),
                        'security_groups': [
                            {'id': sg.get('GroupId', 'Unknown'), 'name': sg.get('GroupName', 'Unknown')}
                            for sg in instance.get('SecurityGroups', [])
                        ],
                        'tags': {tag.get('Key', 'Unknown'): tag.get('Value', 'Unknown') 
                                for tag in instance.get('Tags', [])},
                        'monitoring': instance.get('Monitoring', {}).get('State', 'Unknown'),
                        'platform': instance.get('Platform', 'Linux/Unix')
                    }
                    instance_details.append(details)
        
        return {
            'type': 'instance_details',
            'data': instance_details,
            'summary': {
                'total_instances': len(instance_details),
                'running_instances': len([i for i in instance_details if i['state'] == 'running']),
                'stopped_instances': len([i for i in instance_details if i['state'] == 'stopped'])
            }
        }
    
    def _process_cost_analysis(self, query: str, aws_data: Dict) -> Dict[str, Any]:
        """Process queries about cost analysis"""
        cost_analysis = {
            'ec2_instances': [],
            'storage_volumes': [],
            'estimated_costs': {}
        }
        
        # EC2 Cost Analysis
        if 'EC2' in aws_data and 'instances' in aws_data['EC2']:
            for reservation in aws_data['EC2']['instances']:
                for instance in reservation.get('Instances', []):
                    instance_type = instance.get('InstanceType', 'Unknown')
                    state = instance.get('State', {}).get('Name', 'Unknown')
                    
                    # Rough cost estimation (this would need real pricing data)
                    cost_tier = self._estimate_cost_tier(instance_type)
                    
                    cost_analysis['ec2_instances'].append({
                        'instance_id': instance.get('InstanceId', 'Unknown'),
                        'instance_type': instance_type,
                        'state': state,
                        'cost_tier': cost_tier,
                        'public_ip': instance.get('PublicIpAddress', 'None'),
                        'running_cost_impact': 'HIGH' if state == 'running' and cost_tier == 'HIGH' else 'MEDIUM' if state == 'running' else 'LOW'
                    })
        
        # Storage Cost Analysis
        if 'EC2' in aws_data and 'volumes' in aws_data['EC2']:
            for volume in aws_data['EC2']['volumes']:
                volume_type = volume.get('VolumeType', 'Unknown')
                size = volume.get('Size', 0)
                state = volume.get('State', 'Unknown')
                
                cost_analysis['storage_volumes'].append({
                    'volume_id': volume.get('VolumeId', 'Unknown'),
                    'volume_type': volume_type,
                    'size_gb': size,
                    'state': state,
                    'cost_impact': 'HIGH' if size > 100 else 'MEDIUM' if size > 20 else 'LOW'
                })
        
        return {
            'type': 'cost_analysis',
            'data': cost_analysis,
            'summary': {
                'high_cost_instances': len([i for i in cost_analysis['ec2_instances'] if i['cost_tier'] == 'HIGH']),
                'running_instances': len([i for i in cost_analysis['ec2_instances'] if i['state'] == 'running']),
                'total_storage_gb': sum(v['size_gb'] for v in cost_analysis['storage_volumes'])
            }
        }
    
    def _process_compliance_check(self, query: str, aws_data: Dict) -> Dict[str, Any]:
        """Process queries about compliance checks"""
        compliance_issues = []
        
        # Check EC2 instances
        if 'EC2' in aws_data and 'instances' in aws_data['EC2']:
            for reservation in aws_data['EC2']['instances']:
                for instance in reservation.get('Instances', []):
                    instance_id = instance.get('InstanceId', 'Unknown')
                    
                    # Check for public IP
                    if instance.get('PublicIpAddress'):
                        compliance_issues.append({
                            'resource_type': 'EC2 Instance',
                            'resource_id': instance_id,
                            'issue': 'Has public IP address',
                            'severity': 'MEDIUM',
                            'recommendation': 'Review if public access is necessary'
                        })
                    
                    # Check for missing tags
                    tags = instance.get('Tags', [])
                    if not tags:
                        compliance_issues.append({
                            'resource_type': 'EC2 Instance',
                            'resource_id': instance_id,
                            'issue': 'No tags defined',
                            'severity': 'LOW',
                            'recommendation': 'Add proper tags for governance'
                        })
        
        # Check Security Groups
        if 'EC2' in aws_data and 'security_groups' in aws_data['EC2']:
            for sg in aws_data['EC2']['security_groups']:
                sg_id = sg.get('GroupId', 'Unknown')
                sg_name = sg.get('GroupName', 'Unknown')
                
                # Check for overly permissive rules
                for rule in sg.get('IpPermissions', []):
                    for ip_range in rule.get('IpRanges', []):
                        if ip_range.get('CidrIp') == '0.0.0.0/0':
                            compliance_issues.append({
                                'resource_type': 'Security Group',
                                'resource_id': f"{sg_name} ({sg_id})",
                                'issue': 'Allows access from anywhere (0.0.0.0/0)',
                                'severity': 'HIGH',
                                'recommendation': 'Restrict source IP ranges'
                            })
        
        return {
            'type': 'compliance_check',
            'data': compliance_issues,
            'summary': {
                'total_issues': len(compliance_issues),
                'high_severity': len([i for i in compliance_issues if i['severity'] == 'HIGH']),
                'medium_severity': len([i for i in compliance_issues if i['severity'] == 'MEDIUM']),
                'low_severity': len([i for i in compliance_issues if i['severity'] == 'LOW'])
            }
        }
    
    def _process_resource_relationships(self, query: str, aws_data: Dict) -> Dict[str, Any]:
        """Process queries about resource relationships"""
        relationships = []
        
        if 'EC2' in aws_data and 'instances' in aws_data['EC2']:
            for reservation in aws_data['EC2']['instances']:
                for instance in reservation.get('Instances', []):
                    instance_id = instance.get('InstanceId', 'Unknown')
                    vpc_id = instance.get('VpcId', 'Unknown')
                    subnet_id = instance.get('SubnetId', 'Unknown')
                    
                    # Instance to VPC relationship
                    relationships.append({
                        'source_type': 'EC2 Instance',
                        'source_id': instance_id,
                        'target_type': 'VPC',
                        'target_id': vpc_id,
                        'relationship_type': 'LOCATED_IN'
                    })
                    
                    # Instance to Subnet relationship
                    relationships.append({
                        'source_type': 'EC2 Instance',
                        'source_id': instance_id,
                        'target_type': 'Subnet',
                        'target_id': subnet_id,
                        'relationship_type': 'LOCATED_IN'
                    })
                    
                    # Instance to Security Group relationships
                    for sg in instance.get('SecurityGroups', []):
                        sg_id = sg.get('GroupId', 'Unknown')
                        relationships.append({
                            'source_type': 'EC2 Instance',
                            'source_id': instance_id,
                            'target_type': 'Security Group',
                            'target_id': sg_id,
                            'relationship_type': 'PROTECTED_BY'
                        })
        
        return {
            'type': 'resource_relationships',
            'data': relationships,
            'summary': {
                'total_relationships': len(relationships),
                'unique_sources': len(set(r['source_id'] for r in relationships)),
                'unique_targets': len(set(r['target_id'] for r in relationships))
            }
        }
    
    def _process_unused_resources(self, query: str, aws_data: Dict) -> Dict[str, Any]:
        """Process queries about unused resources"""
        unused_resources = []
        
        # Check for stopped instances
        if 'EC2' in aws_data and 'instances' in aws_data['EC2']:
            for reservation in aws_data['EC2']['instances']:
                for instance in reservation.get('Instances', []):
                    state = instance.get('State', {}).get('Name', 'Unknown')
                    if state == 'stopped':
                        unused_resources.append({
                            'resource_type': 'EC2 Instance',
                            'resource_id': instance.get('InstanceId', 'Unknown'),
                            'issue': 'Instance is stopped',
                            'potential_saving': 'Consider terminating if not needed',
                            'last_activity': str(instance.get('StateTransitionReason', 'Unknown'))
                        })
        
        # Check for unattached volumes
        if 'EC2' in aws_data and 'volumes' in aws_data['EC2']:
            for volume in aws_data['EC2']['volumes']:
                state = volume.get('State', 'Unknown')
                if state == 'available':  # Unattached
                    unused_resources.append({
                        'resource_type': 'EBS Volume',
                        'resource_id': volume.get('VolumeId', 'Unknown'),
                        'issue': 'Volume is not attached to any instance',
                        'potential_saving': f"Storage cost for {volume.get('Size', 0)}GB",
                        'volume_type': volume.get('VolumeType', 'Unknown')
                    })
        
        return {
            'type': 'unused_resources',
            'data': unused_resources,
            'summary': {
                'total_unused': len(unused_resources),
                'stopped_instances': len([r for r in unused_resources if r['resource_type'] == 'EC2 Instance']),
                'unattached_volumes': len([r for r in unused_resources if r['resource_type'] == 'EBS Volume'])
            }
        }
    
    def _estimate_cost_tier(self, instance_type: str) -> str:
        """Estimate cost tier based on instance type"""
        if not instance_type or instance_type == 'Unknown':
            return 'UNKNOWN'
        
        # Rough categorization
        if any(size in instance_type for size in ['nano', 'micro', 'small']):
            return 'LOW'
        elif any(size in instance_type for size in ['medium', 'large']):
            return 'MEDIUM'
        else:
            return 'HIGH'
    
    def format_results_for_display(self, results: Dict[str, Any]) -> str:
        """Format complex query results for display"""
        if results['type'] == 'ec2_with_security_groups':
            return self._format_ec2_with_security_groups(results)
        elif results['type'] == 'security_group_usage':
            return self._format_security_group_usage(results)
        elif results['type'] == 'vpc_resources':
            return self._format_vpc_resources(results)
        elif results['type'] == 'instance_details':
            return self._format_instance_details(results)
        elif results['type'] == 'cost_analysis':
            return self._format_cost_analysis(results)
        elif results['type'] == 'compliance_check':
            return self._format_compliance_check(results)
        elif results['type'] == 'resource_relationships':
            return self._format_resource_relationships(results)
        elif results['type'] == 'unused_resources':
            return self._format_unused_resources(results)
        else:
            return "Results not available for display"
    
    def _format_ec2_with_security_groups(self, results: Dict[str, Any]) -> str:
        """Format EC2 with security groups results"""
        output = []
        output.append("# EC2 Instances with Security Groups\n")
        
        for instance in results['data']:
            output.append(f"## Instance: {instance['instance_id']} ({instance['instance_type']})")
            output.append(f"**State:** {instance['state']}")
            output.append(f"**Public IP:** {instance['public_ip']}")
            output.append(f"**Private IP:** {instance['private_ip']}")
            output.append(f"**VPC:** {instance['vpc_id']}")
            output.append(f"**Subnet:** {instance['subnet_id']}")
            output.append("\n**Security Groups:**")
            
            for sg in instance['security_groups']:
                output.append(f"- {sg['name']} ({sg['id']})")
            
            output.append("\n---\n")
        
        output.append(f"\n## Summary")
        output.append(f"- **Total Instances:** {results['summary']['total_instances']}")
        output.append(f"- **Unique Security Groups:** {results['summary']['unique_security_groups_count']}")
        output.append(f"\n**All Security Groups Used:**")
        for sg in results['unique_security_groups']:
            output.append(f"- {sg}")
        
        return '\n'.join(output)
    
    def _format_security_group_usage(self, results: Dict[str, Any]) -> str:
        """Format security group usage results"""
        output = []
        output.append("# Security Group Usage Analysis\n")
        
        usage_map = results['data']['usage_map']
        all_sgs = results['data']['all_security_groups']
        unused_sgs = results['data']['unused_security_groups']
        
        output.append("## Used Security Groups\n")
        for sg_id, usage_list in usage_map.items():
            sg_info = all_sgs.get(sg_id, {})
            output.append(f"### {sg_info.get('name', 'Unknown')} ({sg_id})")
            output.append(f"**Description:** {sg_info.get('description', 'No description')}")
            output.append(f"**VPC:** {sg_info.get('vpc_id', 'Unknown')}")
            output.append(f"**Used by {len(usage_list)} resource(s):**")
            
            for usage in usage_list:
                output.append(f"- {usage['resource_type']}: {usage['resource_id']} - {usage['resource_details']}")
            
            output.append("\n")
        
        if unused_sgs:
            output.append("## Unused Security Groups\n")
            for sg in unused_sgs:
                output.append(f"- **{sg['name']}** ({sg['id']}) - {sg['description']}")
        
        output.append(f"\n## Summary")
        output.append(f"- **Total Security Groups:** {results['summary']['total_security_groups']}")
        output.append(f"- **Used Security Groups:** {results['summary']['used_security_groups']}")
        output.append(f"- **Unused Security Groups:** {results['summary']['unused_security_groups']}")
        
        return '\n'.join(output)
    
    def _format_vpc_resources(self, results: Dict[str, Any]) -> str:
        """Format VPC resources results"""
        output = []
        output.append("# VPC Resources Analysis\n")
        
        for vpc_id, resources in results['data'].items():
            output.append(f"## VPC: {vpc_id}")
            
            vpc_info = resources.get('vpc_info', {})
            output.append(f"**CIDR Block:** {vpc_info.get('cidr_block', 'Unknown')}")
            output.append(f"**State:** {vpc_info.get('state', 'Unknown')}")
            output.append(f"**Is Default:** {vpc_info.get('is_default', False)}")
            
            # Instances
            instances = resources.get('instances', [])
            if instances:
                output.append(f"\n**EC2 Instances ({len(instances)}):**")
                for instance in instances:
                    output.append(f"- {instance['instance_id']} ({instance['instance_type']}) - {instance['state']}")
            
            # Subnets
            subnets = resources.get('subnets', [])
            if subnets:
                output.append(f"\n**Subnets ({len(subnets)}):**")
                for subnet in subnets:
                    output.append(f"- {subnet['subnet_id']} ({subnet['cidr_block']}) - AZ: {subnet['availability_zone']}")
            
            # Security Groups
            security_groups = resources.get('security_groups', [])
            if security_groups:
                output.append(f"\n**Security Groups ({len(security_groups)}):**")
                for sg in security_groups:
                    output.append(f"- {sg['group_name']} ({sg['group_id']})")
            
            output.append("\n---\n")
        
        output.append(f"## Summary")
        output.append(f"- **Total VPCs:** {results['summary']['total_vpcs']}")
        output.append(f"- **Total Instances:** {results['summary']['total_instances']}")
        output.append(f"- **Total Subnets:** {results['summary']['total_subnets']}")
        
        return '\n'.join(output)
    
    def _format_instance_details(self, results: Dict[str, Any]) -> str:
        """Format instance details results"""
        output = []
        output.append("# EC2 Instance Details\n")
        
        for instance in results['data']:
            output.append(f"## {instance['instance_id']} ({instance['instance_type']})")
            output.append(f"**State:** {instance['state']}")
            output.append(f"**Launch Time:** {instance['launch_time']}")
            output.append(f"**Availability Zone:** {instance['availability_zone']}")
            output.append(f"**Public IP:** {instance['public_ip']}")
            output.append(f"**Private IP:** {instance['private_ip']}")
            output.append(f"**VPC:** {instance['vpc_id']}")
            output.append(f"**Subnet:** {instance['subnet_id']}")
            output.append(f"**Key Pair:** {instance['key_name']}")
            output.append(f"**Platform:** {instance['platform']}")
            output.append(f"**Monitoring:** {instance['monitoring']}")
            
            if instance['security_groups']:
                output.append("\n**Security Groups:**")
                for sg in instance['security_groups']:
                    output.append(f"- {sg['name']} ({sg['id']})")
            
            if instance['tags']:
                output.append("\n**Tags:**")
                for key, value in instance['tags'].items():
                    output.append(f"- {key}: {value}")
            
            output.append("\n---\n")
        
        output.append(f"## Summary")
        output.append(f"- **Total Instances:** {results['summary']['total_instances']}")
        output.append(f"- **Running Instances:** {results['summary']['running_instances']}")
        output.append(f"- **Stopped Instances:** {results['summary']['stopped_instances']}")
        
        return '\n'.join(output)
    
    def _format_cost_analysis(self, results: Dict[str, Any]) -> str:
        """Format cost analysis results"""
        output = []
        output.append("# Cost Analysis\n")
        
        output.append("## EC2 Instances Cost Analysis\n")
        for instance in results['data']['ec2_instances']:
            output.append(f"### {instance['instance_id']} ({instance['instance_type']})")
            output.append(f"**State:** {instance['state']}")
            output.append(f"**Cost Tier:** {instance['cost_tier']}")
            output.append(f"**Running Cost Impact:** {instance['running_cost_impact']}")
            output.append(f"**Public IP:** {instance['public_ip']}")
            output.append("")
        
        output.append("## Storage Cost Analysis\n")
        for volume in results['data']['storage_volumes']:
            output.append(f"### {volume['volume_id']} ({volume['volume_type']})")
            output.append(f"**Size:** {volume['size_gb']} GB")
            output.append(f"**State:** {volume['state']}")
            output.append(f"**Cost Impact:** {volume['cost_impact']}")
            output.append("")
        
        output.append(f"## Summary")
        output.append(f"- **High Cost Instances:** {results['summary']['high_cost_instances']}")
        output.append(f"- **Running Instances:** {results['summary']['running_instances']}")
        output.append(f"- **Total Storage:** {results['summary']['total_storage_gb']} GB")
        
        return '\n'.join(output)
    
    def _format_compliance_check(self, results: Dict[str, Any]) -> str:
        """Format compliance check results"""
        output = []
        output.append("# Compliance Check Results\n")
        
        issues_by_severity = {'HIGH': [], 'MEDIUM': [], 'LOW': []}
        for issue in results['data']:
            issues_by_severity[issue['severity']].append(issue)
        
        for severity in ['HIGH', 'MEDIUM', 'LOW']:
            if issues_by_severity[severity]:
                output.append(f"## {severity} Severity Issues\n")
                for issue in issues_by_severity[severity]:
                    output.append(f"### {issue['resource_type']}: {issue['resource_id']}")
                    output.append(f"**Issue:** {issue['issue']}")
                    output.append(f"**Recommendation:** {issue['recommendation']}")
                    output.append("")
        
        output.append(f"## Summary")
        output.append(f"- **Total Issues:** {results['summary']['total_issues']}")
        output.append(f"- **High Severity:** {results['summary']['high_severity']}")
        output.append(f"- **Medium Severity:** {results['summary']['medium_severity']}")
        output.append(f"- **Low Severity:** {results['summary']['low_severity']}")
        
        return '\n'.join(output)
    
    def _format_resource_relationships(self, results: Dict[str, Any]) -> str:
        """Format resource relationships results"""
        output = []
        output.append("# Resource Relationships\n")
        
        # Group relationships by type
        relationships_by_type = defaultdict(list)
        for rel in results['data']:
            rel_type = rel['relationship_type']
            relationships_by_type[rel_type].append(rel)
        
        for rel_type, relationships in relationships_by_type.items():
            output.append(f"## {rel_type} Relationships\n")
            for rel in relationships:
                output.append(f"- {rel['source_type']} `{rel['source_id']}` → {rel['target_type']} `{rel['target_id']}`")
            output.append("")
        
        output.append(f"## Summary")
        output.append(f"- **Total Relationships:** {results['summary']['total_relationships']}")
        output.append(f"- **Unique Sources:** {results['summary']['unique_sources']}")
        output.append(f"- **Unique Targets:** {results['summary']['unique_targets']}")
        
        return '\n'.join(output)
    
    def _format_unused_resources(self, results: Dict[str, Any]) -> str:
        """Format unused resources results"""
        output = []
        output.append("# Unused Resources Analysis\n")
        
        for resource in results['data']:
            output.append(f"## {resource['resource_type']}: {resource['resource_id']}")
            output.append(f"**Issue:** {resource['issue']}")
            output.append(f"**Potential Saving:** {resource['potential_saving']}")
            
            if 'last_activity' in resource:
                output.append(f"**Last Activity:** {resource['last_activity']}")
            if 'volume_type' in resource:
                output.append(f"**Volume Type:** {resource['volume_type']}")
            
            output.append("")
        
        output.append(f"## Summary")
        output.append(f"- **Total Unused Resources:** {results['summary']['total_unused']}")
        output.append(f"- **Stopped Instances:** {results['summary']['stopped_instances']}")
        output.append(f"- **Unattached Volumes:** {results['summary']['unattached_volumes']}")
        
        return '\n'.join(output)


# Global instance
complex_query_processor = ComplexQueryProcessor()
