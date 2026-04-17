variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "cloudcostiq"
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "RDS allocated storage in GB"
  type        = number
  default     = 20
}

variable "db_master_username" {
  description = "RDS master username"
  type        = string
  default     = "cloudcostiq"
}

variable "db_master_password" {
  description = "RDS master password"
  type        = string
  sensitive   = true
}

variable "frontend_image" {
  description = "Frontend ECR image URL"
  type        = string
}

variable "backend_image" {
  description = "Backend ECR image URL"
  type        = string
}

variable "backend_secret_key" {
  description = "Secret key for JWT"
  type        = string
  sensitive   = true
}