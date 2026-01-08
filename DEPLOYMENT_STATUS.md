# Deployment Status

## Current Status

### ✅ Completed
1. **ECR Repositories Created**
   - Frontend: `808055627316.dkr.ecr.us-east-1.amazonaws.com/cantonese-word-game-frontend`
   - Backend: `808055627316.dkr.ecr.us-east-1.amazonaws.com/cantonese-word-game-backend`

2. **Frontend Image Built and Pushed**
   - Image tags: `302f9b1`, `latest`
   - Status: ✅ Successfully pushed to ECR
   - Pushed at: 2026-01-08T00:09:54

3. **Dockerfiles Fixed**
   - Frontend: Fixed npm install and terser minification
   - Backend: Fixed uv.lock file copying

### ⏳ Pending
1. **Backend Image Build**
   - Status: Blocked by Docker daemon not running
   - Action needed: Start Docker Desktop and rebuild

2. **Infrastructure Deployment**
   - ECS Cluster: Not created yet
   - RDS Database: Not created yet
   - ALB: Not created yet
   - Action needed: Deploy CDK stack

## Next Steps

### Step 1: Start Docker and Build Backend
```bash
# Start Docker Desktop, then:
cd /Users/kelvinchan/dev/test/cantonese-word-game
docker build -t 808055627316.dkr.ecr.us-east-1.amazonaws.com/cantonese-word-game-backend:302f9b1 \
  -t 808055627316.dkr.ecr.us-east-1.amazonaws.com/cantonese-word-game-backend:latest \
  -f backend/Dockerfile backend/

# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin 808055627316.dkr.ecr.us-east-1.amazonaws.com

# Push backend image
docker push 808055627316.dkr.ecr.us-east-1.amazonaws.com/cantonese-word-game-backend:302f9b1
docker push 808055627316.dkr.ecr.us-east-1.amazonaws.com/cantonese-word-game-backend:latest
```

### Step 2: Deploy Infrastructure

#### Option A: Using CDK (Recommended)
```bash
# Install CDK dependencies
cd infrastructure/cdk
pip install -r requirements.txt

# Bootstrap CDK (first time only)
cdk bootstrap

# Deploy infrastructure
cdk deploy
```

#### Option B: Manual AWS Console
Create the following resources manually:
- VPC with public/private subnets
- RDS PostgreSQL instance
- ECS Fargate cluster
- ECS task definitions for frontend and backend
- ECS services
- Application Load Balancer
- Security groups
- IAM roles

### Step 3: Configure Secrets
```bash
# Get RDS endpoint after deployment
RDS_ENDPOINT=$(aws rds describe-db-instances --region us-east-1 \
  --query 'DBInstances[?contains(DBInstanceIdentifier, `cantonese`)].Endpoint.Address' \
  --output text)

# Generate secret key
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Update Secrets Manager
aws secretsmanager put-secret-value \
  --secret-id cantonese-word-game-secrets \
  --secret-string "{
    \"SECRET_KEY\": \"$SECRET_KEY\",
    \"DATABASE_URL\": \"postgresql://username:password@$RDS_ENDPOINT:5432/cantonese_game\",
    \"CORS_ORIGINS\": \"[\\\"http://localhost:5173\\\", \\\"http://localhost:3000\\\"]\"
  }" \
  --region us-east-1
```

### Step 4: Update ECS Services
After infrastructure is deployed:
```bash
# Force new deployment to use latest images
aws ecs update-service \
  --cluster cantonese-word-game-cluster \
  --service cantonese-word-game-frontend-service \
  --force-new-deployment \
  --region us-east-1

aws ecs update-service \
  --cluster cantonese-word-game-cluster \
  --service cantonese-word-game-backend-service \
  --force-new-deployment \
  --region us-east-1
```

## Quick Deploy Script

Once Docker is running, you can use:
```bash
./scripts/deploy.sh
```

This will:
1. Build both images
2. Push to ECR
3. Update ECS services

## Verification

Check deployment status:
```bash
# List ECS services
aws ecs list-services --cluster cantonese-word-game-cluster --region us-east-1

# Get service status
aws ecs describe-services \
  --cluster cantonese-word-game-cluster \
  --services cantonese-word-game-frontend-service cantonese-word-game-backend-service \
  --region us-east-1

# Get Load Balancer DNS
aws elbv2 describe-load-balancers \
  --region us-east-1 \
  --query 'LoadBalancers[?LoadBalancerName==`cantonese-word-game-alb`].DNSName' \
  --output text
```

