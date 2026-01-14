variable "aws_profile" {
  description = "AWS profile to use for authentication"
  type        = string
  # No default - must be explicitly specified
}

variable "aws_region" {
  description = "AWS region for the backend resources"
  type        = string
  default     = "us-west-2"
}

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "allowability"
}
