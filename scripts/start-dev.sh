#!/bin/bash
set -e

echo "=========================================="
echo "Starting Minimal Dev Infrastructure"
echo "=========================================="

cd terraform

# Initialize if needed
if [ ! -d ".terraform" ]; then
  echo "Initializing Terraform..."
  terraform init
fi

# Apply dev configuration
echo "Applying dev configuration (minimal cost)..."
terraform apply -var-file="dev.tfvars" -auto-approve

echo ""
echo "✅ Dev infrastructure ready!"
echo ""
echo "Cost: ~$0-5/month"
echo ""
echo "Next steps:"
echo "1. Run backend locally:"
echo "   cd backend && python -m venv venv && source venv/bin/activate"
echo "   pip install -r requirements.txt"
echo "   uvicorn app.main:app --reload"
echo ""
echo "2. Run frontend locally (in another terminal):"
echo "   cd frontend && npm install"
echo "   npm start"
echo ""
echo "3. Access at: http://localhost:3000"

