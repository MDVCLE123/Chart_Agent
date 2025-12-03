#!/bin/bash
set -e

echo "=========================================="
echo "Pulumi Stack Teardown"
echo "=========================================="

# Ask which stack to tear down
echo "Which stack do you want to tear down?"
echo "  1) dev"
echo "  2) testing"
echo "  3) both"
read -p "Enter choice (1-3): " choice

cd infrastructure

# Activate Python virtual environment
if [ -d "venv" ]; then
  source venv/bin/activate
fi

teardown_stack() {
  local stack_name=$1
  echo ""
  echo "⚠️  This will DELETE all infrastructure in stack: $stack_name"
  read -p "Are you sure? Type 'yes' to confirm: " confirm
  
  if [ "$confirm" = "yes" ]; then
    echo ""
    echo "Deleting Pulumi stack: $stack_name..."
    pulumi stack select $stack_name
    pulumi destroy --yes
    
    read -p "Remove stack from Pulumi? (yes/no): " remove
    if [ "$remove" = "yes" ]; then
      pulumi stack rm $stack_name --yes
      echo "✅ Stack $stack_name deleted and removed!"
    else
      echo "✅ Stack $stack_name destroyed (but still in Pulumi)!"
    fi
  else
    echo "Teardown cancelled for $stack_name"
  fi
}

case $choice in
  1)
    teardown_stack "dev"
    ;;
  2)
    teardown_stack "testing"
    ;;
  3)
    teardown_stack "dev"
    teardown_stack "testing"
    ;;
  *)
    echo "Invalid choice"
    exit 1
    ;;
esac

echo ""
echo "✅ Teardown complete! Cost: $0/month"
echo ""
echo "Note: ECR repositories are retained to preserve Docker images."
echo "To delete them manually:"
echo "  pulumi stack select dev"
echo "  pulumi destroy --yes --remove"
echo ""
