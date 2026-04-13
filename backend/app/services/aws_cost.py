# Serviço de consulta de custos AWS via Cost Explorer API
# Suporta modo mock para desenvolvimento sem credenciais

import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import boto3
from botocore.exceptions import ClientError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AWSCostService:
    # Inicializa o serviço de custos AWS
    # Usa credenciais do ambiente ou entra em modo mock
    def __init__(self):
        self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.aws_region = os.getenv("AWS_REGION", "us-east-1")
        
        # Verifica se as credenciais AWS estão configuradas
        if not self.aws_access_key_id or not self.aws_secret_access_key:
            logger.warning("AWS credentials not configured - using mock data")
            self.mock_mode = True
        else:
            self.mock_mode = False
            # Cria cliente do AWS Cost Explorer com as credenciais fornecidas
            self.ce_client = boto3.client(
                'ce',
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.aws_region
            )
    
    # Gera dados simulados para desenvolvimentolocal sem credenciais AWS
    def _get_mock_data(self) -> Dict[str, Any]:
        from datetime import datetime, timedelta
        import random
        
        services = ["EC2", "RDS", "S3", "Lambda", "Data Transfer"]
        today = datetime.utcnow()
        
        daily_costs = []
        for i in range(30):
            # Gera custos para cada um dos últimos 30 dias
            day = today - timedelta(days=29 - i)
            day_cost = {}
            for service in services:
                base_cost = {
                    "EC2": 150,
                    "RDS": 80,
                    "S3": 25,
                    "Lambda": 15,
                    "Data Transfer": 30
                }
                # Aplica variação aleatória de 80% a 130% do custo base
                variance = random.uniform(0.8, 1.3)
                day_cost[service] = round(base_cost[service] * variance, 2)
            daily_costs.append({
                "date": day.strftime("%Y-%m-%d"),
                "costs": day_cost,
                "total": sum(day_cost.values())
            })
        
        return {
            "daily_costs": daily_costs,
            "services": services,
            "month_to_date": sum(d["total"] for d in daily_costs)
        }
    
    # Consulta custos eusage da AWS para um período específico
    def get_cost_and_usage(self, start_date: str, end_date: str, granularity: str = "DAILY") -> Dict[str, Any]:
        # Em modo mock, retorna dados simulados
        if self.mock_mode:
            return self._get_mock_data()
        
        try:
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date,
                    'End': end_date
                },
                Granularity=granularity,
                Metrics=['UnblendedCost'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'}
                ]
            )
            
            daily_costs = []
            for result in response['ResultsByTime']:
                costs_by_service = {}
                for group in result['Groups']:
                    service = group['Keys'][0]
                    amount = float(group['Metrics']['UnblendedCost']['Amount'])
                    if amount > 0:
                        costs_by_service[service] = round(amount, 2)
                
                daily_costs.append({
                    "date": result['TimePeriod']['Start'],
                    "costs": costs_by_service,
                    "total": sum(costs_by_service.values())
                })
            
            # Extrai lista única de serviços
            services = []
            for dc in daily_costs:
                for svc in dc["costs"].keys():
                    if svc not in services:
                        services.append(svc)
            
            return {
                "daily_costs": daily_costs,
                "services": services,
                "month_to_date": sum(d["total"] for d in daily_costs)
            }
            
        except ClientError as e:
            logger.error(f"AWS API error: {e}")
            return self._get_mock_data()
    
    # Retorna gastos agregados por serviço AWS
    def get_spend_by_service(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        if self.mock_mode:
            mock = self._get_mock_data()
            result = []
            for service in mock["services"]:
                total = sum(d["costs"].get(service, 0) for d in mock["daily_costs"])
                result.append({"service": service, "cost": round(total, 2)})
            return result
        
        try:
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date,
                    'End': end_date
                },
                Granularity='MONTHLY',
                Metrics=['UnblendedCost'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'}
                ]
            )
            
            result = []
            for group in response['ResultsByTime'][0]['Groups']:
                service = group['Keys'][0]
                cost = float(group['Metrics']['UnblendedCost']['Amount'])
                result.append({"service": service, "cost": round(cost, 2)})
            
            return sorted(result, key=lambda x: x["cost"], reverse=True)
            
        except ClientError as e:
            logger.error(f"AWS API error: {e}")
            return []
    
    # Retorna tendência de custos diários dos últimos N dias
    def get_daily_cost_trend(self, days: int = 30) -> Dict[str, Any]:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        return self.get_cost_and_usage(
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d"),
            "DAILY"
        )
    
    # Retorna os N recursos mais caros
    def get_top_resources(self, limit: int = 5) -> List[Dict[str, Any]]:
        if self.mock_mode:
            resources = [
                {"resource_id": "i-0abc123def456789a", "service": "EC2", "cost": 245.50},
                {"resource_id": "db-prod-01", "service": "RDS", "cost": 180.25},
                {"resource_id": "cloudcostiq-bucket", "service": "S3", "cost": 85.00},
                {"resource_id": "arn:aws:lambda:us-east-1:123456789:function:processor", "service": "Lambda", "cost": 45.75},
                {"resource_id": "nat-gateway-01", "service": "Data Transfer", "cost": 32.50},
            ]
            return resources[:limit]
        
        try:
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d"),
                    'End': datetime.utcnow().strftime("%Y-%m-%d")
                },
                Granularity='DAILY',
                Metrics=['UnblendedCost'],
                GroupBy=[
                    {'Type': 'TAG', 'Key': 'RESOURCE_ID'}
                ]
            )
            
            resources = []
            for result in response['ResultsByTime']:
                for group in result['Groups']:
                    resource_id = group['Keys'][0] if group['Keys'][0] else 'Unknown'
                    cost = float(group['Metrics']['UnblendedCost']['Amount'])
                    if cost > 0:
                        resources.append({
                            "resource_id": resource_id,
                            "cost": round(cost, 2)
                        })
            
            # Ordena por custo decrescente e limita resultados
            resources = sorted(resources, key=lambda x: x["cost"], reverse=True)
            return resources[:limit]
            
        except ClientError as e:
            logger.error(f"AWS API error: {e}")
            return []

# Instância global do serviço de custos
aws_cost_service = AWSCostService()