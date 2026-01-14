output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "vpc_cidr" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "IDs of public subnets"
  value       = aws_subnet.public[*].id
}

output "app_subnet_ids" {
  description = "IDs of private app subnets"
  value       = aws_subnet.app[*].id
}

output "db_subnet_ids" {
  description = "IDs of private DB subnets"
  value       = aws_subnet.db[*].id
}

output "public_route_table_id" {
  description = "ID of the public route table"
  value       = aws_route_table.public.id
}

output "app_route_table_id" {
  description = "ID of the app route table"
  value       = aws_route_table.app.id
}

output "db_route_table_id" {
  description = "ID of the DB route table"
  value       = aws_route_table.db.id
}

output "internet_gateway_id" {
  description = "ID of the Internet Gateway"
  value       = aws_internet_gateway.main.id
}

output "availability_zones" {
  description = "Availability zones used for subnets"
  value       = [for i in range(2) : data.aws_availability_zones.available.names[i]]
}
