import os
import boto3
from typing import List, Dict, Any
from datetime import datetime
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)

REQUIRED_TAGS = ["projeto", "ambiente", "gerenciado-por"]

class TagComplianceService:
    def __init__(self):
        self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.aws_region = os.getenv("AWS_REGION", "us-east-1")
        
        if not self.aws_access_key_id or not self.aws_secret_access_key:
            self.mock_mode = True
        else:
            self.mock_mode = False
            self.ce_client = boto3.client(
                'ce',
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.aws_region
            )
            self.resource_client = boto3.client(
                'resourcegroupstaggingapi',
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.aws_region
            )
    
    def _get_mock_data(self) -> List[Dict[str, Any]]:
        return [
            {
                "resource_id": "i-0abc123def456789a",
                "resource_name": "web-server-prod",
                "resource_type": "EC2",
                "service": "EC2",
                "missing_tags": ["ambiente"]
            },
            {
                "resource_id": "rds-prod-cluster-01",
                "resource_name": "prod-database",
                "resource_type": "RDS",
                "service": "RDS",
                "missing_tags": ["gerenciado-por"]
            },
            {
                "resource_id": "lambda-processor-func",
                "resource_name": "data-processor",
                "resource_type": "Lambda",
                "service": "Lambda",
                "missing_tags": []
            },
            {
                "resource_id": "s3-noncompliant-bucket",
                "resource_name": "assets-uploads",
                "resource_type": "S3",
                "service": "S3",
                "missing_tags": ["projeto", "ambiente", "gerenciado-por"]
            }
        ]
    
    def scan_tag_compliance(self) -> List[Dict[str, Any]]:
        if self.mock_mode:
            return self._get_mock_data()
        
        try:
            resources = []
            paginator = self.resource_client.get_paginator('get_resources')
            
            for page in paginator.paginate():
                for resource in page['ResourceTagMappingList']:
                    resource_arn = resource['ResourceARN']
                    tags = {tag['Key']: tag['Value'] for tag in resource.get('Tags', [])}
                    
                    missing_tags = [tag for tag in REQUIRED_TAGS if tag not in tags]
                    
                    if missing_tags:
                        service = self._extract_service_from_arn(resource_arn)
                        resource_type = self._extract_type_from_arn(resource_arn)
                        resource_name = resource_arn.split(':')[-1].split('/')[-1] if '/' in resource_arn else resource_arn.split(':')[-1]
                        
                        resources.append({
                            "resource_id": resource_arn,
                            "resource_name": resource_name,
                            "resource_type": resource_type,
                            "service": service,
                            "missing_tags": missing_tags
                        })
            
            return resources
            
        except ClientError as e:
            logger.error(f"AWS API error: {e}")
            return self._get_mock_data()
    
    def _extract_service_from_arn(self, arn: str) -> str:
        try:
            parts = arn.split(':')
            service = parts[2] if len(parts) > 2 else "Unknown"
            return service.upper()
        except Exception:
            return "Unknown"
    
    def _extract_type_from_arn(self, arn: str) -> str:
        try:
            if ':s3::' in arn:
                return "S3"
            parts = arn.split(':')
            if len(parts) > 5:
                return parts[5].split('/')[0] if '/' in parts[5] else parts[5]
            return "Unknown"
        except Exception:
            return "Unknown"
    
    def get_compliance_summary(self) -> Dict[str, Any]:
        resources = self.scan_tag_compliance()
        
        total_resources = len(resources)
        compliant_resources = sum(1 for r in resources if not r["missing_tags"])
        non_compliant_resources = total_resources - compliant_resources
        
        by_service = {}
        for r in resources:
            svc = r["service"]
            if svc not in by_service:
                by_service[svc] = {"total": 0, "non_compliant": 0}
            by_service[svc]["total"] += 1
            if r["missing_tags"]:
                by_service[svc]["non_compliant"] += 1
        
        return {
            "total_resources": total_resources,
            "compliant_resources": compliant_resources,
            "non_compliant_resources": non_compliant_resources,
            "compliance_percentage": round((compliant_resources / total_resources * 100) if total_resources > 0 else 100, 2),
            "by_service": by_service
        }

tag_compliance_service = TagComplianceService()
