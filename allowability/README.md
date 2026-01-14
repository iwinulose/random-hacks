# Allowability - AWS Fargate Infrastructure

This project deploys a containerized Flask application on AWS using Fargate, with a complete infrastructure setup including VPC, ALB, ECS, and VPC endpoints.

## Architecture

- **VPC**: Multi-AZ setup with public and private subnets
- **ALB**: Internet-facing Application Load Balancer
- **ECS Fargate**: Containerized application in private subnets
- **VPC Endpoints**: Uses VPC endpoints for AWS services
- **ECR**: Container registry with lifecycle policies
- **Security**: Zero-trust network design with security groups

## Project Structure

```
.
├── app/                          # Flask application
│   ├── app.py                    # Application code
│   ├── requirements.txt          # Python dependencies
│   └── Dockerfile                # Container definition
├── terraform/
│   ├── bootstrap/                # Phase 0: Backend setup
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── README.md
│   ├── modules/                  # Reusable Terraform modules
│   │   ├── network/              # VPC, subnets, IGW, route tables
│   │   ├── security_groups/      # Security group definitions
│   │   ├── vpc_endpoints/        # VPC interface and gateway endpoints
│   │   ├── ecr/                  # Container registry
│   │   ├── alb/                  # Application Load Balancer
│   │   └── ecs/                  # ECS cluster, task, and service
│   └── envs/
│       └── dev/                  # Dev environment configuration
│           ├── main.tf           # Module orchestration
│           ├── variables.tf      # Input variables
│           ├── outputs.tf        # Output values
│           ├── backend.tf        # S3 backend configuration
│           └── terraform.tfvars.example
└── README.md
```

## Prerequisites

- AWS CLI configured with named profiles in `~/.aws/credentials`
- Terraform >= 1.0
- Docker
- Access to an AWS account with appropriate permissions

## Quick Start

### Phase 0: Bootstrap Terraform Backend

First, create the S3 bucket and DynamoDB table for Terraform state:

```bash
cd terraform/bootstrap

# Copy and configure variables
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars and set your AWS profile (REQUIRED)

# Initialize and apply
terraform init
terraform apply
```

Note the outputs (`s3_bucket_name` and `dynamodb_table_name`).

### Phase 1: Deploy Infrastructure

1. **Configure variables**

   ```bash
   cd terraform/envs/dev
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars and set your AWS profile (REQUIRED)
   ```

2. **Update backend configuration**

   Edit `terraform/envs/dev/backend.tf` and replace the placeholders with actual values from bootstrap outputs:

   ```hcl
   terraform {
     backend "s3" {
       bucket         = "allowability-tfstate-123456789012-us-west-2"  # From bootstrap output
       key            = "envs/dev/terraform.tfstate"
       region         = "us-west-2"
       dynamodb_table = "allowability-tfstate-lock"  # From bootstrap output
       encrypt        = true
       profile        = "your-aws-profile-name"  # Same as in terraform.tfvars
     }
   }
   ```
   2. **Create terraform.tfvars** (optional)

   ```bash
   cd terraform/envs/dev
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars as needed
   ```

3. **Deploy infrastructure without ECS service**

   ```bash
   cd terraform/envs/dev
   terraform init
   terraform apply -var="enable_service=false"
   ```

   Note the `ecr_repository_url` output.

4. **Build and push Docker image**

   ```bash
   # From the project root
   cd app
   
   # Login to ECR (use your AWS profile)
   aws ecr get-login-password --region us-west-2 --profile your-aws-profile-name | \
     docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-west-2.amazonaws.com
   
   # Build image
   docker build -t allowability:latest .
   
   # Tag image
   docker tag allowability:latest <ecr-repository-url>:latest
   
   # Push image
   docker push <ecr-repository-url>:latest
   ```

5. **Enable ECS service**

   Edit `terraform/envs/dev/terraform.tfvars` and set `enable_service = true`, then:

   ```bash
   cd terraform/envs/dev
   terraform apply
   ```

   Note the `alb_dns_name` output.

6. **Test the deployment**

   Wait 2-3 minutes for the ECS tasks to become healthy, then:

   ```bash
   curl http://<alb-dns-name>/health
   # Expected: {"status":"ok","message":"Hello world!","timestamp":"..."}
   ```

## Configuration

### Key Variables

Edit `terraform/envs/dev/terraform.tfvars` to customize:

- `aws_profile`: AWS profile name from `~/.aws/credentials` (no default)
- `aws_region`: AWS region (default: `us-west-2`)
- `project_name`: Project name (default: `allowability`)
- `vpc_cidr`: VPC CIDR block (default: `10.0.0.0/16`)
- `container_port`: Application port (default: `8080`)
- `ecs_task_cpu`: CPU units (default: `256` = 0.25 vCPU)
- `ecs_task_memory`: Memory in MB (default: `512`)
- `ecs_desired_count`: Number of tasks (default: `2`)
- `enable_service`: Enable ECS service (default: `false`)

### Network Design

**Public Subnets** (2 AZs):
- `10.0.1.0/24` - us-west-2a
- `10.0.2.0/24` - us-west-2b
- Used by: ALB

**Private App Subnets** (2 AZs):
- `10.0.11.0/24` - us-west-2a
- `10.0.12.0/24` - us-west-2b
- Used by: ECS tasks, VPC endpoints

**Private DB Subnets** (2 AZs, reserved for Phase 2):
- `10.0.21.0/24` - us-west-2a
- `10.0.22.0/24` - us-west-2b
- Used by: Aurora (Phase 2)

## Features

### Security
- ECS tasks in private subnets with no public IPs
- Security groups with least-privilege access
- VPC endpoints instead of NAT Gateway (no internet egress)
- ALB as single entry point from internet
- S3 state encryption and versioning

### High Availability
- Multi-AZ deployment
- ALB health checks
- ECS service auto-recovery
- Rolling deployments with zero downtime

### Cost Optimization
- No NAT Gateway (~$32/month saved)
- VPC endpoints for AWS services (~$36/month flat)
- Fargate spot pricing ready
- Aurora Serverless v2 ready (Phase 2)

### Observability
- CloudWatch Container Insights enabled
- Application logs to CloudWatch
- ECS task health checks
- ALB access logs ready

## Cost Estimate

Monthly costs (us-west-2, Phase 1):

| Service | Cost |
|---------|------|
| ALB | ~$16.20 |
| Fargate (2 tasks, 0.25 vCPU, 512 MB) | ~$21.18 |
| VPC Endpoints (5 endpoints) | ~$36.00 |
| ECR Storage (~10 GB) | ~$1.00 |
| **Total** | **~$75/month** |

*Excludes data transfer costs (first 100 GB free)*

## Monitoring

### View ECS service status
```bash
aws ecs describe-services \
  --cluster allowability-cluster-dev \
  --services allowability-service-dev \
  --region us-west-2
```

### View CloudWatch logs
```bash
aws logs tail /ecs/allowability-dev --follow --region us-west-2
```

### View ALB target health
```bash
aws elbv2 describe-target-health \
  --target-group-arn <target-group-arn> \
  --region us-west-2
```

## Troubleshooting

### ECS tasks fail to start

1. Check CloudWatch logs: `/ecs/allowability-dev`
2. Verify ECR image exists and is accessible
3. Check VPC endpoint connectivity
4. Verify security group rules

### ALB returns 503

1. Check ECS task health status
2. Verify target group health checks
3. Check security group rules (ALB → ECS)
4. Ensure tasks are running in correct subnets

### Cannot pull from ECR

1. Verify VPC endpoints are working (`ecr.api`, `ecr.dkr`, `s3`)
2. Check ECS task execution role permissions
3. Verify security group allows HTTPS to endpoints

## Cleanup

To destroy all resources:

```bash
# Destroy main infrastructure
cd terraform/envs/dev
terraform destroy

# Destroy bootstrap (optional, only if you're sure)
cd ../../bootstrap
terraform destroy
```

**Warning**: This will delete all resources including the S3 state bucket!

## Phase 2 (Future)

The architecture is designed to accommodate Phase 2 with minimal changes:

- Aurora PostgreSQL Serverless v2 in DB subnets
- RDS Proxy in app subnets
- Secrets Manager for DB credentials
- Additional security groups for DB access
- Flask `/dbtest` endpoint for DB validation

## Technologies

- **Infrastructure**: Terraform 1.0+, AWS Provider 6.28.0+
- **Container**: Docker
- **Application**: Python 3.11, Flask 3.0, Gunicorn 21.2
- **AWS Services**: VPC, ECS Fargate, ALB, ECR, CloudWatch, S3, DynamoDB

## License

This project is for demonstration purposes.

## Support

For issues or questions, please refer to the AWS documentation or Terraform registry.
