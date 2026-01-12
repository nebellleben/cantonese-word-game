# Cantonese Word Game - AWS CDK Infrastructure

This directory contains AWS CDK code to deploy the Cantonese Word Game infrastructure on AWS with HTTPS support and custom domain.

## Prerequisites

1. AWS CLI configured with appropriate credentials
2. AWS CDK CLI installed: `npm install -g aws-cdk`
3. Python 3.11+
4. Docker (for building images)
5. Domain name registered (or ready to configure nameservers)

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
- `domain_name`: Your root domain (default: "flumenlucidum.com")
- `subdomain_name`: Application subdomain (default: "app")
- VPC CIDR block
- RDS instance type
- ECS task CPU and memory
- Desired service count

Example configuration:
```json
{
  "context": {
    "domain_name": "yourdomain.com",
    "subdomain_name": "app",
    "db_instance_type": "db.t3.small",
    "desired_count": 2
  }
}
```

Or pass context values:
```bash
cdk deploy --context domain_name=yourdomain.com --context desired_count=3
```

## Resources Created

### Core Infrastructure
- **VPC** with public and private subnets
- **RDS PostgreSQL** instance for production database
- **ECS Fargate** cluster with frontend and backend services
- **Application Load Balancer** with HTTPS listeners
- **Security Groups** for network isolation
- **IAM Roles** for service permissions

### Domain & Networking
- **Route 53 Hosted Zone** for your domain
- **A Record** pointing to the Load Balancer
- **ACM Certificate** with automatic DNS validation
- **HTTP to HTTPS redirect** on port 80
- **Path-based routing**:
  - `/api/*` → Backend service (port 8443)
  - All other paths → Frontend service (port 443)

### Storage & Monitoring
- **ECR repositories** for Docker images
- **CloudWatch** log groups and dashboard
- **Secrets Manager** secret for sensitive data
- **SSM Parameter Store** for ALB DNS and configuration

## Outputs

After deployment, the stack outputs:
- **DomainName**: Full domain name (e.g., "app.flumenlucidum.com")
- **HostedZoneId**: Route 53 hosted zone ID
- **Nameservers**: Nameservers to configure at your domain registrar
- **LoadBalancerDNS**: ALB DNS name (for reference)
- **FrontendECRRepository**: ECR repository URI for frontend
- **BackendECRRepository**: ECR repository URI for backend
- **DatabaseEndpoint**: RDS PostgreSQL endpoint
- **SecretsManagerSecret**: ARN of the Secrets Manager secret
- **CloudWatchDashboard**: URL to CloudWatch dashboard

## Domain Setup

### 1. Configure Nameservers

After deployment, update your domain registrar's nameservers with the values from the stack output:

```bash
# Get nameservers from stack output
aws cloudformation describe-stacks \
  --stack-name CantoneseWordGameStack \
  --query 'Stacks[0].Outputs[?OutputKey==`Nameservers`].OutputValue' \
  --output text
```

Or check `deployment-outputs.json` for the `Nameservers` field.

### 2. Wait for DNS Propagation

The ACM certificate validation happens automatically via DNS records. This typically takes 30 minutes to a few hours depending on your registrar.

### 3. Verify Certificate Status

```bash
aws acm describe-certificate \
  --certificate-arn <certificate-arn-from-outputs>
```

## HTTPS Configuration

The infrastructure automatically:
- Creates an ACM certificate for your domain
- Validates it via DNS records in Route 53
- Configures HTTPS listeners on the ALB (ports 443, 8443)
- Sets up HTTP to HTTPS redirects (ports 80, 8000)
- Updates CORS configuration for the custom domain

## Accessing the Application

After deployment and DNS propagation:
- **Frontend**: `https://app.yourdomain.com`
- **Backend API**: `https://app.yourdomain.com/api`
- **API Docs**: `https://app.yourdomain.com/api/docs`

## Monitoring

Access the CloudWatch Dashboard:
- URL: Available in stack outputs as `CloudWatchDashboard`
- Or navigate in AWS Console: CloudWatch → Dashboards → CantoneseWordGame-Dashboard

The dashboard includes:
- ECS service CPU and memory utilization
- RDS CPU and connections
- ALB request count and response time
- Target health status

## Cleanup

To destroy all resources:
```bash
cdk destroy
```

**Warning**: This will delete all resources including:
- The database and all data
- Route 53 hosted zone
- SSL certificates
- All application configurations

Ensure you have backups before destroying!

## Troubleshooting

### Certificate Validation Fails
- Verify nameservers are configured correctly at your registrar
- Wait for DNS propagation (can take up to 48 hours)
- Check Route 53 for the validation records

### Cannot Access Application via Custom Domain
- Check DNS propagation: `nslookup app.yourdomain.com`
- Verify ALB target groups are healthy
- Check security group rules allow HTTPS (443) from your IP
- Review CloudWatch logs for ECS tasks

### CORS Errors
- Verify the custom domain matches the `CORS_ORIGINS` environment variable
- Check Secrets Manager configuration includes your custom domain
- Ensure the frontend is making requests to the correct domain

