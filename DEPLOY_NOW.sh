#!/bin/bash
# Complete deployment script for Cantonese Word Game
# Run this after starting Docker Desktop

set -e

echo "🚀 Starting Cantonese Word Game Deployment"
echo "=========================================="

# Configuration
AWS_REGION="us-east-1"
AWS_ACCOUNT_ID="808055627316"
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
IMAGE_TAG=$(git rev-parse --short HEAD 2>/dev/null || echo "latest")

echo "Region: ${AWS_REGION}"
echo "Account ID: ${AWS_ACCOUNT_ID}"
echo "Image Tag: ${IMAGE_TAG}"
echo ""

# Check Docker
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ Error: AWS credentials not configured. Run 'aws configure' first."
    exit 1
fi

echo "✅ Docker is running"
echo "✅ AWS credentials configured"
echo ""

# Step 1: Login to ECR
echo "📦 Step 1: Logging in to ECR..."
aws ecr get-login-password --region ${AWS_REGION} | \
    docker login --username AWS --password-stdin ${ECR_REGISTRY}
echo "✅ Logged in to ECR"
echo ""

# Step 2: Build and push frontend
echo "🏗️  Step 2: Building frontend image..."
docker build -t ${ECR_REGISTRY}/cantonese-word-game-frontend:${IMAGE_TAG} \
             -t ${ECR_REGISTRY}/cantonese-word-game-frontend:latest \
             -f Dockerfile .

echo "📤 Pushing frontend image..."
docker push ${ECR_REGISTRY}/cantonese-word-game-frontend:${IMAGE_TAG}
docker push ${ECR_REGISTRY}/cantonese-word-game-frontend:latest
echo "✅ Frontend image pushed"
echo ""

# Step 3: Build and push backend
echo "🏗️  Step 3: Building backend image..."
docker build -t ${ECR_REGISTRY}/cantonese-word-game-backend:${IMAGE_TAG} \
             -t ${ECR_REGISTRY}/cantonese-word-game-backend:latest \
             -f backend/Dockerfile backend/

echo "📤 Pushing backend image..."
docker push ${ECR_REGISTRY}/cantonese-word-game-backend:${IMAGE_TAG}
docker push ${ECR_REGISTRY}/cantonese-word-game-backend:latest
echo "✅ Backend image pushed"
echo ""

# Step 4: Check if infrastructure exists
echo "🔍 Step 4: Checking infrastructure..."
CLUSTER_EXISTS=$(aws ecs describe-clusters --clusters cantonese-word-game-cluster --region ${AWS_REGION} 2>&1 | grep -q "cantonese-word-game-cluster" && echo "yes" || echo "no")

if [ "$CLUSTER_EXISTS" = "no" ]; then
    echo "⚠️  Infrastructure not deployed yet."
    echo ""
    echo "To deploy infrastructure, run:"
    echo "  cd infrastructure/cdk"
    echo "  pip install -r requirements.txt"
    echo "  cdk bootstrap  # First time only"
    echo "  cdk deploy"
    echo ""
    echo "Or use the setup script:"
    echo "  ./scripts/setup-aws.sh"
    echo ""
    echo "After infrastructure is deployed, run this script again to update services."
    exit 0
fi

# Step 5: Update ECS services
echo "🔄 Step 5: Updating ECS services..."
aws ecs update-service \
    --cluster cantonese-word-game-cluster \
    --service cantonese-word-game-frontend-service \
    --force-new-deployment \
    --region ${AWS_REGION} > /dev/null
echo "✅ Frontend service update initiated"

aws ecs update-service \
    --cluster cantonese-word-game-cluster \
    --service cantonese-word-game-backend-service \
    --force-new-deployment \
    --region ${AWS_REGION} > /dev/null
echo "✅ Backend service update initiated"
echo ""

# Step 6: Wait for services to stabilize
echo "⏳ Step 6: Waiting for services to stabilize..."
aws ecs wait services-stable \
    --cluster cantonese-word-game-cluster \
    --services cantonese-word-game-frontend-service \
    --region ${AWS_REGION}
echo "✅ Frontend service is stable"

aws ecs wait services-stable \
    --cluster cantonese-word-game-cluster \
    --services cantonese-word-game-backend-service \
    --region ${AWS_REGION}
echo "✅ Backend service is stable"
echo ""

# Step 7: Get Load Balancer DNS
echo "🌐 Step 7: Getting Load Balancer DNS..."
ALB_DNS=$(aws elbv2 describe-load-balancers \
    --region ${AWS_REGION} \
    --query 'LoadBalancers[?LoadBalancerName==`cantonese-word-game-alb`].DNSName' \
    --output text 2>/dev/null || echo "Not found")

if [ "$ALB_DNS" != "Not found" ] && [ ! -z "$ALB_DNS" ]; then
    echo ""
    echo "✅ Deployment Complete!"
    echo "================================"
    echo "Frontend URL: http://${ALB_DNS}"
    echo "Backend API: http://${ALB_DNS}:8000/api"
    echo "API Docs: http://${ALB_DNS}:8000/docs"
    echo ""
else
    echo "⚠️  Load Balancer DNS not found. Check AWS Console."
fi

echo ""
echo "📊 View logs in CloudWatch:"
echo "  Frontend: /ecs/cantonese-word-game-frontend"
echo "  Backend: /ecs/cantonese-word-game-backend"
echo ""
echo "📈 View dashboard:"
echo "  https://console.aws.amazon.com/cloudwatch/home?region=${AWS_REGION}#dashboards:name=CantoneseWordGame-Dashboard"

