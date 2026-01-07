#!/bin/bash
# Deployment script for Cantonese Word Game
# This script builds Docker images, pushes to ECR, and updates ECS services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
AWS_REGION="${AWS_REGION:-us-east-1}"
AWS_ACCOUNT_ID="${AWS_ACCOUNT_ID:-$(aws sts get-caller-identity --query Account --output text)}"
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
ECR_REPOSITORY_FRONTEND="cantonese-word-game-frontend"
ECR_REPOSITORY_BACKEND="cantonese-word-game-backend"
ECS_CLUSTER="cantonese-word-game-cluster"
ECS_SERVICE_FRONTEND="cantonese-word-game-frontend-service"
ECS_SERVICE_BACKEND="cantonese-word-game-backend-service"

# Get the current commit SHA for tagging
IMAGE_TAG="${IMAGE_TAG:-$(git rev-parse --short HEAD)}"

echo -e "${GREEN}Starting deployment...${NC}"
echo "Region: ${AWS_REGION}"
echo "Account ID: ${AWS_ACCOUNT_ID}"
echo "Image Tag: ${IMAGE_TAG}"

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}Error: AWS CLI is not configured. Please run 'aws configure'${NC}"
    exit 1
fi

# Login to ECR
echo -e "${YELLOW}Logging in to ECR...${NC}"
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}

# Build and push frontend image
echo -e "${YELLOW}Building frontend image...${NC}"
docker build -t ${ECR_REGISTRY}/${ECR_REPOSITORY_FRONTEND}:${IMAGE_TAG} \
             -t ${ECR_REGISTRY}/${ECR_REPOSITORY_FRONTEND}:latest \
             -f Dockerfile .

echo -e "${YELLOW}Pushing frontend image...${NC}"
docker push ${ECR_REGISTRY}/${ECR_REPOSITORY_FRONTEND}:${IMAGE_TAG}
docker push ${ECR_REGISTRY}/${ECR_REPOSITORY_FRONTEND}:latest

# Build and push backend image
echo -e "${YELLOW}Building backend image...${NC}"
docker build -t ${ECR_REGISTRY}/${ECR_REPOSITORY_BACKEND}:${IMAGE_TAG} \
             -t ${ECR_REGISTRY}/${ECR_REPOSITORY_BACKEND}:latest \
             -f backend/Dockerfile \
             backend/

echo -e "${YELLOW}Pushing backend image...${NC}"
docker push ${ECR_REGISTRY}/${ECR_REPOSITORY_BACKEND}:${IMAGE_TAG}
docker push ${ECR_REGISTRY}/${ECR_REPOSITORY_BACKEND}:latest

# Update ECS services
echo -e "${YELLOW}Updating ECS frontend service...${NC}"
aws ecs update-service \
    --cluster ${ECS_CLUSTER} \
    --service ${ECS_SERVICE_FRONTEND} \
    --force-new-deployment \
    --region ${AWS_REGION} \
    > /dev/null

echo -e "${YELLOW}Updating ECS backend service...${NC}"
aws ecs update-service \
    --cluster ${ECS_CLUSTER} \
    --service ${ECS_SERVICE_BACKEND} \
    --force-new-deployment \
    --region ${AWS_REGION} \
    > /dev/null

# Wait for services to stabilize
echo -e "${YELLOW}Waiting for frontend service to stabilize...${NC}"
aws ecs wait services-stable \
    --cluster ${ECS_CLUSTER} \
    --services ${ECS_SERVICE_FRONTEND} \
    --region ${AWS_REGION}

echo -e "${YELLOW}Waiting for backend service to stabilize...${NC}"
aws ecs wait services-stable \
    --cluster ${ECS_CLUSTER} \
    --services ${ECS_SERVICE_BACKEND} \
    --region ${AWS_REGION}

echo -e "${GREEN}Deployment completed successfully!${NC}"
echo "Frontend image: ${ECR_REGISTRY}/${ECR_REPOSITORY_FRONTEND}:${IMAGE_TAG}"
echo "Backend image: ${ECR_REGISTRY}/${ECR_REPOSITORY_BACKEND}:${IMAGE_TAG}"

