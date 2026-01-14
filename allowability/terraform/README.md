# Terraform Infrastructure

This directory contains all Terraform code for deploying the Allowability infrastructure on AWS.

## Directory Structure

```
terraform/
├── bootstrap/          # Phase 0: S3 and DynamoDB for Terraform state
├── modules/           # Reusable infrastructure modules
│   ├── network/       # VPC, subnets, IGW, route tables
│   ├── security_groups/  # Security group definitions
│   ├── vpc_endpoints/    # VPC interface and gateway endpoints
│   ├── ecr/           # Elastic Container Registry
│   ├── alb/           # Application Load Balancer
│   └── ecs/           # ECS Fargate cluster, tasks, and service
└── envs/
    └── dev/           # Development environment
```

## Module Overview

### Network Module
Creates the VPC foundation with:
- 1 VPC (10.0.0.0/16)
- 6 subnets across 2 AZs (public, private app, private db)
- Internet Gateway
- Route tables with appropriate routes

### Security Groups Module
Defines security groups for:
- ALB (ingress from internet, egress to app)
- ECS tasks (ingress from ALB, egress to VPC endpoints)
- VPC endpoints (ingress from ECS tasks)

### VPC Endpoints Module
Creates AWS service endpoints to avoid NAT Gateway:
- S3 (gateway endpoint)
- ECR API, ECR Docker (interface endpoints)
- CloudWatch Logs (interface endpoint)
- STS (interface endpoint)
- Secrets Manager (interface endpoint, for Phase 2)

### ECR Module
Container registry with:
- Scan on push enabled
- Lifecycle policies (keep last 10 images, expire untagged after 7 days)
- AES256 encryption

### ALB Module
Internet-facing Application Load Balancer with:
- HTTP listener on port 80
- Target group for ECS tasks (IP target type)
- Health checks on `/health` endpoint

### ECS Module
Fargate deployment with:
- ECS cluster with Container Insights
- Task definition (0.25 vCPU, 512 MB)
- ECS service (conditionally created via `enable_service` variable)
- IAM roles (task execution and task)
- CloudWatch log group

## Module Dependencies

```
network (independent)
    ↓
security_groups → vpc_endpoints
    ↓                ↓
   alb          → ecs
    ↓                ↓
   └────────────────┘

ecr (independent) → ecs
```

## Usage

### Prerequisites

- AWS CLI configured with named profiles in `~/.aws/credentials`
- Terraform >= 1.0 installed
- Appropriate AWS permissions

### Bootstrap (One-time setup)

```bash
cd terraform/bootstrap

# Copy and configure variables
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars and set aws_profile

# Initialize and apply
terraform init
terraform apply
# Note the outputs for backend configuration
```

### Environment Deployment

```bash
cd terraform/envs/dev

# Copy and configure variables
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars and set aws_profile

# Update backend.tf with the profile and backend info from bootstrap outputs

# Initialize with backend
terraform init

# Plan changes
terraform plan

# Apply infrastructure (service disabled initially)
terraform apply

# After pushing Docker image to ECR, enable the service
# Edit terraform.tfvars and set enable_service = true
terraform apply
```

## Variables

### Common Variables (in envs/dev/variables.tf)

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `aws_profile` | string | **(none)** | **REQUIRED**: AWS profile name from `~/.aws/credentials` |
| `aws_region` | string | `us-west-2` | AWS region |
| `environment` | string | `dev` | Environment name |
| `project_name` | string | `allowability` | Project name |
| `vpc_cidr` | string | `10.0.0.0/16` | VPC CIDR block |
| `container_port` | number | `8080` | Container port |
| `enable_service` | bool | `false` | Create ECS service |
| `image_tag` | string | `latest` | Docker image tag |
| `ecs_task_cpu` | number | `256` | Task CPU units |
| `ecs_task_memory` | number | `512` | Task memory (MB) |
| `ecs_desired_count` | number | `2` | Number of tasks |

## Outputs

Key outputs from the dev environment:

- `alb_dns_name`: ALB endpoint for accessing the application
- `ecr_repository_url`: ECR repository URL for pushing images
- `vpc_id`: VPC identifier
- `ecs_cluster_name`: ECS cluster name
- `ecs_service_name`: ECS service name (empty if not created)
- `log_group_name`: CloudWatch log group name

## Best Practices

### State Management
- Bootstrap creates S3 backend for state storage
- State is encrypted and versioned
- DynamoDB provides state locking
- Never commit `terraform.tfstate` to Git

### Security
- Use least-privilege IAM policies
- Security groups follow principle of least privilege
- VPC endpoints prevent internet egress
- Secrets should use AWS Secrets Manager (Phase 2)

### Tagging
- Provider-level default tags applied automatically
- Resource-specific tags for identification
- Environment tag for resource organization

### Module Design
- Modules are reusable and environment-agnostic
- Outputs clearly document exported values
- Variables have sensible defaults
- Dependencies explicitly declared

## Provider Configuration

Using AWS Provider 6.28.0+ with:
- Provider-level default tagging
- Latest resource configurations
- Improved type safety

```hcl
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 6.28.0, < 7.0.0"
    }
  }
}
```

## Extending

### Adding a new environment

1. Copy `envs/dev` to `envs/prod`
2. Update `backend.tf` with unique state key and profile
3. Customize `terraform.tfvars` (including `aws_profile` - REQUIRED)
4. Apply: `terraform apply`

### Adding new modules

1. Create module directory under `modules/`
2. Add `main.tf`, `variables.tf`, `outputs.tf`
3. Reference from environment's `main.tf`
4. Document in this README

## Troubleshooting

### State Lock Issues
```bash
# Force unlock if process was interrupted
terraform force-unlock <lock-id>
```

### Backend Migration
```bash
# If changing backends
terraform init -migrate-state
```

### Module Changes
```bash
# Reinitialize after module changes
terraform init -upgrade
```

## Validation

```bash
# Format code
terraform fmt -recursive

# Validate configuration
terraform validate

# Check for security issues (if using tfsec)
tfsec .
```
