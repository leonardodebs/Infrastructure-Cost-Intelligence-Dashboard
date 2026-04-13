terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

data "aws_caller_identity" "current" {}

resource "aws_iam_role" "cloudcostiq_cost_reader" {
  name = "CloudCostIQ-CostReaderRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = ["ecs-tasks.amazonaws.com", "eks.amazonaws.com"]
        }
        Condition = {
          StringEquals = {
            "aws:SourceAccount" : data.aws_caller_identity.current.account_id
          }
        }
      }
    ]
  })

  tags = {
    Name        = "CloudCost IQ Cost Reader Role"
    Environment = "production"
    ManagedBy   = "Terraform"
  }
}

resource "aws_iam_policy" "cloudcostiq_cost_explorer" {
  name = "CloudCostIQ-CostExplorerReadOnly"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ce:GetCostAndUsage",
          "ce:GetTags",
          "ce:GetDimensionValues",
          "ce:GetReservationUtilization",
          "ce:GetCoverage",
          "ce:GetCostForecast"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "organizations:ListAccounts",
          "organizations:DescribeOrganization"
        ]
        Resource = "*"
      }
    ]
  })

  tags = {
    Name        = "CloudCost IQ Cost Explorer Policy"
    Environment = "production"
  }
}

resource "aws_iam_role_policy_attachment" "cloudcostiq_cost_reader_attach" {
  role       = aws_iam_role.cloudcostiq_cost_reader.name
  policy_arn = aws_iam_policy.cloudcostiq_cost_explorer.arn
}

resource "aws_iam_policy" "cloudcostiq_tag_compliance" {
  name = "CloudCostIQ-TagComplianceReadOnly"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "resourcegroupstaggingapi:GetResources",
          "resourcegroupstaggingapi:GetTagKeys",
          "resourcegroupstaggingapi:GetTagValues"
        ]
        Resource = "*"
      }
    ]
  })

  tags = {
    Name        = "CloudCost IQ Tag Compliance Policy"
    Environment = "production"
  }
}

resource "aws_iam_role_policy_attachment" "cloudcostiq_tag_reader_attach" {
  role       = aws_iam_role.cloudcostiq_cost_reader.name
  policy_arn = aws_iam_policy.cloudcostiq_tag_compliance.arn
}

output "iam_role_arn" {
  value = aws_iam_role.cloudcostiq_cost_reader.arn
}

output "iam_role_name" {
  value = aws_iam_role.cloudcostiq_cost_reader.name
}
