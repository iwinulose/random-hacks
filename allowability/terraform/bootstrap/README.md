# Bootstrap - Terraform Backend

This directory contains the Terraform configuration to create the S3 bucket and DynamoDB table required for storing Terraform state for the main infrastructure.

## Purpose

The bootstrap stack creates:
- **S3 Bucket**: Stores Terraform state files with versioning and encryption
- **DynamoDB Table**: Provides state locking to prevent concurrent modifications

## Prerequisites

- AWS CLI configured with named profiles in `~/.aws/credentials`
- Terraform >= 1.0 installed
- Appropriate AWS permissions to create S3 buckets and DynamoDB tables

## Usage

### 1. Configure variables

Copy the example variables file and customize it:

```bash
cd terraform/bootstrap
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` and set your AWS profile:

```hcl
aws_profile  = "your-aws-profile-name"
aws_region   = "us-west-2"
project_name = "allowability"
```

### 2. Initialize Terraform

```bash
terraform init
```

### 3. Review the plan

```bash
terraform plan
```

### 4. Apply the configuration

```bash
terraform apply
```

### 5. Note the outputs

After successful apply, note the output values:
- `s3_bucket_name`: Use this in your backend configuration
- `dynamodb_table_name`: Use this in your backend configuration

Example output:
```
s3_bucket_name = "allowability-tfstate-123456789012-us-west-2"
dynamodb_table_name = "allowability-tfstate-lock"
```

### 6. Update main infrastructure backend config

Copy the bucket name and DynamoDB table name to `terraform/envs/dev/backend.tf`:

```hcl
terraform {
  backend "s3" {
    bucket         = "allowability-tfstate-123456789012-us-west-2"  # From output
    key            = "envs/dev/terraform.tfstate"
    region         = "us-west-2"
    dynamodb_table = "allowability-tfstate-lock"  # From output
    encrypt        = true
    profile        = "your-aws-profile-name"  # Same as used in terraform.tfvars
  }
}
```

## State Management

This bootstrap configuration does NOT use a remote backend itself. The Terraform state for the bootstrap stack will be stored locally in `terraform.tfstate`. 

**Important**: Keep the bootstrap state file safe! Consider:
- Committing it to a private repository with encryption
- Storing it in a secure location
- Backing it up regularly

If you lose the bootstrap state file, you can import the existing resources:
```bash
terraform import aws_s3_bucket.tfstate allowability-tfstate-123456789012-us-west-2
terraform import aws_dynamodb_table.tfstate_lock allowability-tfstate-lock
```

## Customization

You can customize the configuration by creating a `terraform.tfvars` file:

```hcl
aws_profile  = "your-aws-profile-name"
aws_region   = "us-west-2"
project_name = "allowability"
```

## Cleanup

To destroy the bootstrap resources (only do this if you're sure you don't need them):

```bash
# First, make sure no other Terraform state is stored in the bucket
terraform destroy
```

**Warning**: Destroying the bootstrap stack will delete all Terraform state files stored in the S3 bucket!
