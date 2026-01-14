# S3 Gateway Endpoint
resource "aws_vpc_endpoint" "s3" {
  vpc_id            = var.vpc_id
  service_name      = "com.amazonaws.${var.aws_region}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = var.route_table_ids

  tags = {
    Name = "${var.project_name}-s3-endpoint-${var.environment}"
    Type = "Gateway"
  }
}

# ECR API Interface Endpoint
resource "aws_vpc_endpoint" "ecr_api" {
  vpc_id              = var.vpc_id
  service_name        = "com.amazonaws.${var.aws_region}.ecr.api"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = var.subnet_ids
  security_group_ids  = [var.endpoints_security_group_id]
  private_dns_enabled = true

  tags = {
    Name    = "${var.project_name}-ecr-api-endpoint-${var.environment}"
    Type    = "Interface"
    Service = "ECR API"
  }
}

# ECR Docker Interface Endpoint
resource "aws_vpc_endpoint" "ecr_dkr" {
  vpc_id              = var.vpc_id
  service_name        = "com.amazonaws.${var.aws_region}.ecr.dkr"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = var.subnet_ids
  security_group_ids  = [var.endpoints_security_group_id]
  private_dns_enabled = true

  tags = {
    Name    = "${var.project_name}-ecr-dkr-endpoint-${var.environment}"
    Type    = "Interface"
    Service = "ECR Docker"
  }
}

# CloudWatch Logs Interface Endpoint
resource "aws_vpc_endpoint" "logs" {
  vpc_id              = var.vpc_id
  service_name        = "com.amazonaws.${var.aws_region}.logs"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = var.subnet_ids
  security_group_ids  = [var.endpoints_security_group_id]
  private_dns_enabled = true

  tags = {
    Name    = "${var.project_name}-logs-endpoint-${var.environment}"
    Type    = "Interface"
    Service = "CloudWatch Logs"
  }
}

# STS Interface Endpoint
resource "aws_vpc_endpoint" "sts" {
  vpc_id              = var.vpc_id
  service_name        = "com.amazonaws.${var.aws_region}.sts"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = var.subnet_ids
  security_group_ids  = [var.endpoints_security_group_id]
  private_dns_enabled = true

  tags = {
    Name    = "${var.project_name}-sts-endpoint-${var.environment}"
    Type    = "Interface"
    Service = "STS"
  }
}

# Secrets Manager Interface Endpoint (for Phase 2)
resource "aws_vpc_endpoint" "secretsmanager" {
  vpc_id              = var.vpc_id
  service_name        = "com.amazonaws.${var.aws_region}.secretsmanager"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = var.subnet_ids
  security_group_ids  = [var.endpoints_security_group_id]
  private_dns_enabled = true

  tags = {
    Name    = "${var.project_name}-secretsmanager-endpoint-${var.environment}"
    Type    = "Interface"
    Service = "Secrets Manager"
  }
}
