#!/bin/bash
set -e

echo "=========================================="
echo "Setting up Pulumi"
echo "=========================================="

echo ""
echo "Pulumi uses Pulumi Cloud (free for individuals) or local storage for state."
echo ""
echo "Options:"
echo "  1. Pulumi Cloud (recommended) - Free for individuals, automatic backups"
echo "  2. Local storage - State files stored locally"
echo "  3. AWS S3 - State files in your own S3 bucket"
echo ""
read -p "Choose option (1-3) [1]: " choice
choice=${choice:-1}

case $choice in
  1)
    echo ""
    echo "Using Pulumi Cloud (default)"
    echo "You'll need to:"
    echo "  1. Create account at: https://app.pulumi.com/signup"
    echo "  2. Run: pulumi login"
    echo ""
    ;;
  2)
    echo ""
    echo "Using local storage"
    pulumi login --local
    echo "✅ Pulumi configured for local storage"
    ;;
  3)
    read -p "Enter S3 bucket name: " bucket_name
    pulumi login s3://$bucket_name
    echo "✅ Pulumi configured for S3 storage"
    ;;
esac

echo ""
echo "Installing Python dependencies..."
cd infrastructure
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo ""
echo "✅ Pulumi setup complete!"
echo ""
echo "Next steps:"
echo "  cd infrastructure"
echo "  pulumi stack select dev    # or: pulumi stack init dev"
echo "  pulumi up                   # Deploy infrastructure"
echo ""

