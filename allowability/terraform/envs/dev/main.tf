terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  profile = var.aws_profile
  region  = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# Network Module
module "network" {
  source = "../../modules/network"

  project_name = var.project_name
  environment  = var.environment
  vpc_cidr     = var.vpc_cidr
}

# Security Groups Module
module "security_groups" {
  source = "../../modules/security_groups"

  project_name   = var.project_name
  environment    = var.environment
  vpc_id         = module.network.vpc_id
  vpc_cidr       = module.network.vpc_cidr
  container_port = var.container_port
}

# VPC Endpoints Module
module "vpc_endpoints" {
  source = "../../modules/vpc_endpoints"

  project_name                = var.project_name
  environment                 = var.environment
  aws_region                  = var.aws_region
  vpc_id                      = module.network.vpc_id
  subnet_ids                  = module.network.app_subnet_ids
  route_table_ids             = [module.network.app_route_table_id, module.network.db_route_table_id]
  endpoints_security_group_id = module.security_groups.endpoints_security_group_id
}

# ECR Module
module "ecr" {
  source = "../../modules/ecr"

  project_name = var.project_name
  environment  = var.environment
}

# ALB Module
module "alb" {
  source = "../../modules/alb"

  project_name           = var.project_name
  environment            = var.environment
  vpc_id                 = module.network.vpc_id
  public_subnet_ids      = module.network.public_subnet_ids
  alb_security_group_id  = module.security_groups.alb_security_group_id
  container_port         = var.container_port
}

# ECS Module
module "ecs" {
  source = "../../modules/ecs"

  project_name          = var.project_name
  environment           = var.environment
  aws_region            = var.aws_region
  ecr_repository_url    = module.ecr.repository_url
  image_tag             = var.image_tag
  container_port        = var.container_port
  task_cpu              = var.ecs_task_cpu
  task_memory           = var.ecs_task_memory
  desired_count         = var.ecs_desired_count
  app_subnet_ids        = module.network.app_subnet_ids
  app_security_group_id = module.security_groups.app_security_group_id
  target_group_arn      = module.alb.target_group_arn
  log_retention_days    = var.log_retention_days
  enable_service        = var.enable_service

  depends_on = [
    module.vpc_endpoints,
    module.alb
  ]
}
