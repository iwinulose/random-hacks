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

variable "vpc_id" {
  description = "ID of the VPC"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs for interface endpoints"
  type        = list(string)
}

variable "route_table_ids" {
  description = "List of route table IDs for gateway endpoints"
  type        = list(string)
}

variable "endpoints_security_group_id" {
  description = "Security group ID for interface endpoints"
  type        = string
}
