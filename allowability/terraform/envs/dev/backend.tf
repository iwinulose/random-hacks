# Backend configuration for Terraform state
# Update the bucket name and profile after running the bootstrap stack
terraform {
  backend "s3" {
    # Replace with actual bucket name from bootstrap outputs
    bucket         = "allowability-tfstate-<account-id>-us-west-2"
    profile        = "your-aws-profile-name"
    key            = "envs/dev/terraform.tfstate"
    region         = "us-west-2"
    dynamodb_table = "allowability-tfstate-lock"
    encrypt        = true
  }
}
