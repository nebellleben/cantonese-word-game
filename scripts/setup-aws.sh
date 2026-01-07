#!/bin/bash
# Initial AWS setup script for Cantonese Word Game
# This script sets up ECR repositories, Secrets Manager, and deploys infrastructure

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
AWS_REGION="${AWS_REGION:-us-east-1}"
AWS_ACCOUNT_ID="${AWS_ACCOUNT_ID:-$(aws sts get-caller-identity --query Account --output text)}"

echo -e "${GREEN}Starting AWS setup...${NC}"
echo "Region: ${AWS_REGION}"
echo "Account ID: ${AWS_ACCOUNT_ID}"

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}Error: AWS CLI is not configured. Please run 'aws configure'${NC}"
    exit 1
fi

# Check if CDK is installed
if ! command -v cdk &> /dev/null; then
    echo -e "${RED}Error: AWS CDK is not installed. Please install with: npm install -g aws-cdk${NC}"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo -e "${RED}Error: Docker is not running. Please start Docker${NC}"
    exit 1
fi

# Step 1: Bootstrap CDK (if not already done)
echo -e "${YELLOW}Step 1: Bootstrapping CDK...${NC}"
cdk bootstrap aws://${AWS_ACCOUNT_ID}/${AWS_REGION} || echo "CDK already bootstrapped"

# Step 2: Install CDK dependencies
echo -e "${YELLOW}Step 2: Installing CDK dependencies...${NC}"
cd infrastructure/cdk
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

# Step 3: Deploy infrastructure
echo -e "${YELLOW}Step 3: Deploying infrastructure with CDK...${NC}"
cdk deploy --require-approval never

# Step 4: Get ECR repository URIs
echo -e "${YELLOW}Step 4: Getting ECR repository information...${NC}"
FRONTEND_REPO=$(aws ecr describe-repositories --repository-names cantonese-word-game-frontend --region ${AWS_REGION} --query 'repositories[0].repositoryUri' --output text)
BACKEND_REPO=$(aws ecr describe-repositories --repository-names cantonese-word-game-backend --region ${AWS_REGION} --query 'repositories[0].repositoryUri' --output text)

echo -e "${GREEN}ECR Repositories created:${NC}"
echo "Frontend: ${FRONTEND_REPO}"
echo "Backend: ${BACKEND_REPO}"

# Step 5: Get Secrets Manager secret ARN
echo -e "${YELLOW}Step 5: Getting Secrets Manager information...${NC}"
SECRET_ARN=$(aws secretsmanager describe-secret --secret-id cantonese-word-game-secrets --region ${AWS_REGION} --query 'ARN' --output text 2>/dev/null || echo "Secret not found")

if [ "$SECRET_ARN" != "Secret not found" ]; then
    echo -e "${GREEN}Secrets Manager secret: ${SECRET_ARN}${NC}"
    echo -e "${YELLOW}Note: Update the secret with your DATABASE_URL and other secrets${NC}"
fi

# Step 6: Get Load Balancer DNS
echo -e "${YELLOW}Step 6: Getting Load Balancer DNS...${NC}"
ALB_DNS=$(aws elbv2 describe-load-balancers --region ${AWS_REGION} --query 'LoadBalancers[?LoadBalancerName==`cantonese-word-game-alb`].DNSName' --output text)

if [ ! -z "$ALB_DNS" ]; then
    echo -e "${GREEN}Load Balancer DNS: ${ALB_DNS}${NC}"
    echo -e "${YELLOW}Frontend URL: http://${ALB_DNS}${NC}"
    echo -e "${YELLOW}Backend API URL: http://${ALB_DNS}:8000${NC}"
fi

# Step 7: Get RDS endpoint
echo -e "${YELLOW}Step 7: Getting RDS endpoint...${NC}"
RDS_ENDPOINT=$(aws rds describe-db-instances --region ${AWS_REGION} --query 'DBInstances[?DBInstanceIdentifier==`cantonesewordgamestack-postgresqlinstance*`].Endpoint.Address' --output text)

if [ ! -z "$RDS_ENDPOINT" ]; then
    echo -e "${GREEN}RDS Endpoint: ${RDS_ENDPOINT}${NC}"
    echo -e "${YELLOW}Note: Update Secrets Manager with the database connection string${NC}"
fi

echo -e "${GREEN}Setup completed!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Update Secrets Manager secret with:"
echo "   - SECRET_KEY (generate with: python -c 'import secrets; print(secrets.token_urlsafe(32))')"
echo "   - DATABASE_URL (postgresql://username:password@${RDS_ENDPOINT}:5432/cantonese_game)"
echo "   - CORS_ORIGINS (JSON array of allowed origins)"
echo ""
echo "2. Build and push Docker images:"
echo "   ./scripts/deploy.sh"
echo ""
echo "3. Or use GitHub Actions for automated CI/CD"

