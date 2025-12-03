#!/bin/bash
set -e

echo "=========================================="
echo "Deploy Updated ECS Services"
echo "=========================================="

STACK_NAME=${1:-testing}
cd infrastructure

# Activate Python virtual environment
if [ -d "venv" ]; then
  source venv/bin/activate
fi

echo "Getting cluster information from Pulumi stack: $STACK_NAME..."

# Select stack
pulumi stack select $STACK_NAME

# Get cluster name from Pulumi outputs
CLUSTER_NAME=$(pulumi stack output ecs_cluster_name)

if [ -z "$CLUSTER_NAME" ]; then
  echo "❌ Could not find ECS cluster in stack: $STACK_NAME"
  echo "Make sure the stack is deployed: ./scripts/start-testing.sh"
  exit 1
fi

echo "ECS Cluster: $CLUSTER_NAME"
echo ""

# Get AWS region from Pulumi config
AWS_REGION=$(pulumi config get aws:region || echo "us-east-1")

# List services in cluster
SERVICES=$(aws ecs list-services \
  --cluster $CLUSTER_NAME \
  --region $AWS_REGION \
  --query 'serviceArns[*]' \
  --output text)

if [ -z "$SERVICES" ]; then
  echo "No ECS services found in cluster."
  echo "Note: ECS services should be defined in infrastructure/__main__.py"
  echo "Update Pulumi code and run: pulumi up"
  exit 0
fi

echo "Forcing new deployment for all services..."
for service_arn in $SERVICES; do
  service_name=$(basename $service_arn)
  echo "  - Updating $service_name..."
  
  aws ecs update-service \
    --cluster $CLUSTER_NAME \
    --service $service_name \
    --force-new-deployment \
    --region $AWS_REGION \
    --output text >/dev/null
done

echo ""
echo "✅ Deployment initiated!"
echo ""
echo "Monitor deployment:"
echo "  aws ecs describe-services --cluster $CLUSTER_NAME --services \$(aws ecs list-services --cluster $CLUSTER_NAME --query 'serviceArns[*]' --output text --region $AWS_REGION) --region $AWS_REGION"
echo ""
