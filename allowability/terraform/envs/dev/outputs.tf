output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  value       = module.alb.alb_dns_name
}

output "ecr_repository_url" {
  description = "URL of the ECR repository"
  value       = module.ecr.repository_url
}

output "vpc_id" {
  description = "ID of the VPC"
  value       = module.network.vpc_id
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = module.ecs.cluster_name
}

output "ecs_service_name" {
  description = "Name of the ECS service (empty if not created)"
  value       = module.ecs.service_name
}

output "log_group_name" {
  description = "Name of the CloudWatch log group"
  value       = module.ecs.log_group_name
}

output "availability_zones" {
  description = "Availability zones used"
  value       = module.network.availability_zones
}
