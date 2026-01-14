variable "aws_profile" {
  description = "AWS profile to use for authentication"
  type        = string
  # No default - must be explicitly specified
}

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-west-2"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "allowability"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "container_port" {
  description = "Port that the container listens on"
  type        = number
  default     = 8080
}

variable "enable_service" {
  description = "Whether to create the ECS service (set to false until ECR image is pushed)"
  type        = bool
  default     = false
}

variable "image_tag" {
  description = "Docker image tag to deploy"
  type        = string
  default     = "latest"
}

variable "ecs_task_cpu" {
  description = "CPU units for the ECS task (256 = .25 vCPU)"
  type        = number
  default     = 256
}

variable "ecs_task_memory" {
  description = "Memory for the ECS task in MB"
  type        = number
  default     = 512
}

variable "ecs_desired_count" {
  description = "Number of ECS task instances to run"
  type        = number
  default     = 2
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 7
}
