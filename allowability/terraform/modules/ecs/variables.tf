variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment name (e.g., dev, staging, prod)"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "ecr_repository_url" {
  description = "URL of the ECR repository"
  type        = string
}

variable "image_tag" {
  description = "Docker image tag to deploy"
  type        = string
  default     = "latest"
}

variable "container_port" {
  description = "Port that the container listens on"
  type        = number
  default     = 8080
}

variable "task_cpu" {
  description = "CPU units for the task (256 = .25 vCPU)"
  type        = number
  default     = 256
}

variable "task_memory" {
  description = "Memory for the task in MB"
  type        = number
  default     = 512
}

variable "desired_count" {
  description = "Number of task instances to run"
  type        = number
  default     = 2
}

variable "app_subnet_ids" {
  description = "List of private app subnet IDs for ECS tasks"
  type        = list(string)
}

variable "app_security_group_id" {
  description = "Security group ID for ECS tasks"
  type        = string
}

variable "target_group_arn" {
  description = "ARN of the ALB target group"
  type        = string
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 7
}

variable "enable_service" {
  description = "Whether to create the ECS service (set to false until ECR image is pushed)"
  type        = bool
  default     = false
}
