# Security Group for ALB
resource "aws_security_group" "alb" {
  name_prefix = "${var.project_name}-alb-${var.environment}-"
  description = "Security group for Application Load Balancer"
  vpc_id      = var.vpc_id

  tags = {
    Name    = "${var.project_name}-alb-sg-${var.environment}"
    Purpose = "ALB"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# ALB Ingress: Allow HTTP from internet
resource "aws_security_group_rule" "alb_ingress_http" {
  type              = "ingress"
  from_port         = 80
  to_port           = 80
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  description       = "Allow HTTP from internet"
  security_group_id = aws_security_group.alb.id
}

# ALB Egress: Allow traffic to app containers
resource "aws_security_group_rule" "alb_egress_to_app" {
  type                     = "egress"
  from_port                = var.container_port
  to_port                  = var.container_port
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.app.id
  description              = "Allow traffic to ECS tasks"
  security_group_id        = aws_security_group.alb.id
}

# Security Group for ECS Tasks
resource "aws_security_group" "app" {
  name_prefix = "${var.project_name}-app-${var.environment}-"
  description = "Security group for ECS tasks"
  vpc_id      = var.vpc_id

  tags = {
    Name    = "${var.project_name}-app-sg-${var.environment}"
    Purpose = "ECS Tasks"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# App Ingress: Allow traffic from ALB
resource "aws_security_group_rule" "app_ingress_from_alb" {
  type                     = "ingress"
  from_port                = var.container_port
  to_port                  = var.container_port
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.alb.id
  description              = "Allow traffic from ALB"
  security_group_id        = aws_security_group.app.id
}

# App Egress: Allow HTTPS to VPC endpoints
resource "aws_security_group_rule" "app_egress_to_endpoints" {
  type                     = "egress"
  from_port                = 443
  to_port                  = 443
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.endpoints.id
  description              = "Allow HTTPS to VPC interface endpoints"
  security_group_id        = aws_security_group.app.id
}

# App Egress: Allow HTTPS to VPC CIDR (for S3 gateway endpoint)
resource "aws_security_group_rule" "app_egress_to_vpc" {
  type              = "egress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  cidr_blocks       = [var.vpc_cidr]
  description       = "Allow HTTPS within VPC (for S3 gateway endpoint)"
  security_group_id = aws_security_group.app.id
}

# Security Group for VPC Interface Endpoints
resource "aws_security_group" "endpoints" {
  name_prefix = "${var.project_name}-endpoints-${var.environment}-"
  description = "Security group for VPC interface endpoints"
  vpc_id      = var.vpc_id

  tags = {
    Name    = "${var.project_name}-endpoints-sg-${var.environment}"
    Purpose = "VPC Interface Endpoints"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Endpoints Ingress: Allow HTTPS from app security group
resource "aws_security_group_rule" "endpoints_ingress_from_app" {
  type                     = "ingress"
  from_port                = 443
  to_port                  = 443
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.app.id
  description              = "Allow HTTPS from ECS tasks"
  security_group_id        = aws_security_group.endpoints.id
}
