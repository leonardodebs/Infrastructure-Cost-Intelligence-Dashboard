output "vpc_id" {
  description = "ID da VPC criada"
  value       = aws_vpc.main.id
}

output "alb_dns_name" {
  description = "URL do Load Balancer (Acesse o projeto por aqui)"
  value       = aws_alb.main.dns_name
}

output "database_endpoint" {
  description = "Endpoint de conexão da base Postgres"
  value       = aws_db_instance.main.endpoint
  sensitive   = true
}

output "ecr_backend_url" {
  description = "URL do repositório ECR do Backend"
  value       = aws_ecr_repository.backend.repository_url
}

output "ecr_frontend_url" {
  description = "URL do repositório ECR do Frontend"
  value       = aws_ecr_repository.frontend.repository_url
}

output "ecs_cluster_name" {
  description = "Nome do Cluster ECS"
  value       = aws_ecs_cluster.main.name
}

output "account_id" {
  description = "ID da Conta AWS utilizada"
  value       = data.aws_caller_identity.current.account_id
}
