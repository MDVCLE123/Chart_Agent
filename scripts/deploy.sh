#!/bin/bash
set -e

echo "=========================================="
echo "Deploying to ECS"
echo "=========================================="

cd terraform

# Get cluster and service names
CLUSTER_NAME=$(terraform output -raw ecs_cluster_name)

echo "ECS Cluster: $CLUSTER_NAME"
echo ""

# Force new deployment for backend
echo "Updating backend service..."
aws ecs update-service \
  --cluster $CLUSTER_NAME \
  --service chart-agent-backend-dev \
  --force-new-deployment \
  --region us-east-1

# Force new deployment for frontend
echo "Updating frontend service..."
aws ecs update-service \
  --cluster $CLUSTER_NAME \
  --service chart-agent-frontend-dev \
  --force-new-deployment \
  --region us-east-1

echo ""
echo "✅ Deployment initiated"
echo ""
echo "Monitor deployment status:"
echo "  aws ecs describe-services --cluster $CLUSTER_NAME --services chart-agent-backend-dev chart-agent-frontend-dev"
echo ""
echo "Or check in AWS Console:"
echo "  https://console.aws.amazon.com/ecs/home?region=us-east-1#/clusters/$CLUSTER_NAME/services"

