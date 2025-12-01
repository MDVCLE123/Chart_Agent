#!/bin/bash
set -e

echo "=========================================="
echo "Building and Pushing Docker Images"
echo "=========================================="

# Get AWS account ID and region
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=${AWS_REGION:-us-east-1}

# ECR repository URLs
ECR_BACKEND="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/chart-agent-backend-dev"
ECR_FRONTEND="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/chart-agent-frontend-dev"

echo "AWS Account: $AWS_ACCOUNT_ID"
echo "Region: $AWS_REGION"
echo "Backend ECR: $ECR_BACKEND"
echo "Frontend ECR: $ECR_FRONTEND"
echo ""

# Login to ECR
echo "Logging in to ECR..."
aws ecr get-login-password --region ${AWS_REGION} | \
  docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# Build and push backend
echo ""
echo "Building backend Docker image..."
docker build -t chart-agent-backend:latest ./backend

echo "Tagging backend image..."
docker tag chart-agent-backend:latest ${ECR_BACKEND}:latest

echo "Pushing backend image to ECR..."
docker push ${ECR_BACKEND}:latest

# Build and push frontend
echo ""
echo "Building frontend Docker image..."
docker build -t chart-agent-frontend:latest ./frontend

echo "Tagging frontend image..."
docker tag chart-agent-frontend:latest ${ECR_FRONTEND}:latest

echo "Pushing frontend image to ECR..."
docker push ${ECR_FRONTEND}:latest

echo ""
echo "✅ Images successfully pushed to ECR"
echo ""
echo "Backend: ${ECR_BACKEND}:latest"
echo "Frontend: ${ECR_FRONTEND}:latest"
echo ""
echo "To deploy these images:"
echo "  1. Update ECS task definitions with new images"
echo "  2. Or run: ./scripts/deploy.sh"

