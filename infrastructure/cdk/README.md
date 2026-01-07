# Cantonese Word Game - AWS CDK Infrastructure

This directory contains AWS CDK code to deploy the Cantonese Word Game infrastructure on AWS.

## Prerequisites

1. AWS CLI configured with appropriate credentials
2. AWS CDK CLI installed: `npm install -g aws-cdk`
3. Python 3.11+
4. Docker (for building images)

## Setup

1. Install Python dependencies:
```bash
cd infrastructure/cdk
pip install -r requirements.txt
```

2. Bootstrap CDK (first time only):
```bash
cdk bootstrap
```

## Deployment

### Deploy all infrastructure:
```bash
cdk deploy
```

### Deploy specific stack:
```bash
cdk deploy CantoneseWordGameStack
```

### View what will be created:
```bash
cdk synth
cdk diff
```

## Configuration

Edit `cdk.json` to configure:
- VPC CIDR block
- RDS instance type
- ECS task CPU and memory
- Desired service count

Or pass context values:
```bash
cdk deploy --context db_instance_type=db.t3.small --context desired_count=3
```

## Resources Created

- VPC with public and private subnets
- RDS PostgreSQL instance
- ECS Fargate cluster
- ECS services for frontend and backend
- Application Load Balancer
- ECR repositories
- Security groups
- IAM roles
- CloudWatch log groups
- Secrets Manager secret

## Outputs

After deployment, the stack outputs:
- Load Balancer DNS name
- ECR repository URIs
- Database endpoint
- Secrets Manager secret ARN

## Cleanup

To destroy all resources:
```bash
cdk destroy
```

**Warning**: This will delete all resources including the database. Make sure you have backups!

