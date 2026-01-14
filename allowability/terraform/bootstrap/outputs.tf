output "s3_bucket_name" {
  description = "Name of the S3 bucket for Terraform state"
  value       = aws_s3_bucket.tfstate.id
}

output "s3_bucket_arn" {
  description = "ARN of the S3 bucket for Terraform state"
  value       = aws_s3_bucket.tfstate.arn
}

output "dynamodb_table_name" {
  description = "Name of the DynamoDB table for state locking"
  value       = aws_dynamodb_table.tfstate_lock.name
}

output "dynamodb_table_arn" {
  description = "ARN of the DynamoDB table for state locking"
  value       = aws_dynamodb_table.tfstate_lock.arn
}

output "backend_config" {
  description = "Backend configuration to use in the main Terraform code"
  value = {
    bucket         = aws_s3_bucket.tfstate.id
    region         = var.aws_region
    dynamodb_table = aws_dynamodb_table.tfstate_lock.name
    encrypt        = true
  }
}
