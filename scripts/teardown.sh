#!/bin/bash
set -e

echo "=========================================="
echo "⚠️  WARNING: Infrastructure Teardown"
echo "=========================================="
echo ""
echo "This will destroy ALL infrastructure including:"
echo "  - VPC and networking"
echo "  - ECS cluster and services"
echo "  - Application Load Balancer"
echo "  - NAT Gateway (if enabled)"
echo "  - CloudWatch logs"
echo ""
echo "Cost after teardown: $0/month"
echo ""

read -p "Are you sure you want to proceed? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
  echo "Teardown cancelled"
  exit 0
fi

cd terraform

echo ""
echo "Destroying infrastructure..."
terraform destroy -auto-approve

echo ""
echo "✅ All resources deleted"
echo ""
echo "Note: The following are preserved:"
echo "  - ECR repositories (contains your Docker images)"
echo "  - Terraform state in S3"
echo ""
echo "To completely clean up:"
echo "  1. Delete ECR repositories manually in AWS Console"
echo "  2. Run: aws s3 rm s3://chart-agent-terraform-state --recursive"
echo "  3. Run: aws s3 rb s3://chart-agent-terraform-state"
echo "  4. Run: aws dynamodb delete-table --table-name terraform-state-lock"

