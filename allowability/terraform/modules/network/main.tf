# Data source to get available AZs
data "aws_availability_zones" "available" {
  state = "available"
}

# VPC
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "${var.project_name}-vpc-${var.environment}"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.project_name}-igw-${var.environment}"
  }
}

# Public Subnets (for ALB)
resource "aws_subnet" "public" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 1)
  availability_zone = data.aws_availability_zones.available.names[count.index]

  map_public_ip_on_launch = true

  tags = {
    Name    = "${var.project_name}-public-${count.index == 0 ? "a" : "b"}-${var.environment}"
    Tier    = "public"
    Purpose = "ALB"
  }
}

# Private App Subnets (for ECS tasks + VPC endpoints)
resource "aws_subnet" "app" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 11)
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name    = "${var.project_name}-app-${count.index == 0 ? "a" : "b"}-${var.environment}"
    Tier    = "private"
    Purpose = "ECS + VPC Endpoints"
  }
}

# Private DB Subnets (reserved for Phase 2)
resource "aws_subnet" "db" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 21)
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name    = "${var.project_name}-db-${count.index == 0 ? "a" : "b"}-${var.environment}"
    Tier    = "private"
    Purpose = "Database"
  }
}

# Route Table for Public Subnets
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.project_name}-public-rt-${var.environment}"
    Tier = "public"
  }
}

# Route to Internet Gateway for Public Subnets
resource "aws_route" "public_internet" {
  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.main.id
}

# Associate Public Subnets with Public Route Table
resource "aws_route_table_association" "public" {
  count          = 2
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# Route Table for App Subnets (no default route - VPC endpoints only)
resource "aws_route_table" "app" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name    = "${var.project_name}-app-rt-${var.environment}"
    Tier    = "private"
    Purpose = "App subnets - VPC endpoints only"
  }
}

# Associate App Subnets with App Route Table
resource "aws_route_table_association" "app" {
  count          = 2
  subnet_id      = aws_subnet.app[count.index].id
  route_table_id = aws_route_table.app.id
}

# Route Table for DB Subnets (no default route)
resource "aws_route_table" "db" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name    = "${var.project_name}-db-rt-${var.environment}"
    Tier    = "private"
    Purpose = "Database subnets"
  }
}

# Associate DB Subnets with DB Route Table
resource "aws_route_table_association" "db" {
  count          = 2
  subnet_id      = aws_subnet.db[count.index].id
  route_table_id = aws_route_table.db.id
}
