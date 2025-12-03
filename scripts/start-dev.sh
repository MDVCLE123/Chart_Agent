#!/bin/bash
set -e

echo "=========================================="
echo "Starting Development Infrastructure"
echo "=========================================="

echo "Deploying Pulumi stack with dev configuration..."
echo "This creates minimal infrastructure (~$0-5/month)"
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

# Select or create dev stack
pulumi stack select dev 2>/dev/null || pulumi stack init dev

# Deploy infrastructure
pulumi up --yes

echo ""
echo "✅ Dev infrastructure ready!"
echo ""
echo "Cost: ~$0-5/month"
echo ""
echo "Next steps:"
echo "  1. Run backend locally: cd backend && uvicorn app.main:app --reload"
echo "  2. Run frontend locally: cd frontend && npm start"
echo ""
echo "View stack: pulumi stack --show-urns"
echo "View outputs: pulumi stack output"
echo ""
