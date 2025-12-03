#!/bin/bash
set -e

echo "=========================================="
echo "Starting Testing Infrastructure"
echo "=========================================="

echo "Deploying Pulumi stack with testing configuration..."
echo "This creates full infrastructure (~$50-70/month)"
echo ""

cd infrastructure

# Activate Python virtual environment
if [ ! -d "venv" ]; then
  echo "Creating Python virtual environment..."
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
else
  source venv/bin/activate
fi

# Select or create testing stack
pulumi stack select testing 2>/dev/null || pulumi stack init testing

# Deploy infrastructure
pulumi up --yes

echo ""
echo "Stack deployed successfully!"
echo ""

# Get outputs
echo "Fetching stack outputs..."
ALB_DNS=$(pulumi stack output alb_dns_name 2>/dev/null || echo "")
ECR_BACKEND=$(pulumi stack output backend_ecr_repository_url)
ECR_FRONTEND=$(pulumi stack output frontend_ecr_repository_url)

echo ""
echo "✅ Testing infrastructure ready!"
echo ""
echo "ECR Backend Repository:  $ECR_BACKEND"
echo "ECR Frontend Repository: $ECR_FRONTEND"

if [ -n "$ALB_DNS" ]; then
  echo "Application URL: http://$ALB_DNS"
fi

echo ""
echo "Next steps:"
echo "  1. Build and push Docker images: ./scripts/build-and-push.sh"
echo "  2. Deploy ECS services with Pulumi (update infrastructure code)"
echo ""
echo "View all outputs: pulumi stack output"
echo ""
