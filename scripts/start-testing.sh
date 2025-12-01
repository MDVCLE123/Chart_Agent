#!/bin/bash
set -e

echo "=========================================="
echo "Starting Full Testing Infrastructure"
echo "=========================================="

cd terraform

# Initialize if needed
if [ ! -d ".terraform" ]; then
  echo "Initializing Terraform..."
  terraform init
fi

# Apply testing configuration
echo "Applying testing configuration (full stack)..."
terraform apply -var-file="testing.tfvars" -auto-approve

# Get AWS account ID and region
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=$(terraform output -raw vpc_id | cut -d: -f4)

# Build and push Docker images
echo ""
echo "Building and pushing Docker images..."
cd ..
./scripts/build-and-push.sh

# Get ALB DNS
cd terraform
ALB_DNS=$(terraform output -raw alb_dns_name)

echo ""
echo "✅ Testing infrastructure ready!"
echo ""
echo "Access your application at:"
echo "  http://$ALB_DNS"
echo ""
echo "Note: It may take 2-3 minutes for services to become healthy"
echo ""
echo "To scale back down when done:"
echo "  ./scripts/start-dev.sh"

