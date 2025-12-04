#!/bin/bash
# Create admin user in Cognito for Chart Agent

set -e

# Configuration - these should match your setup
REGION="${COGNITO_REGION:-${AWS_REGION:-us-east-1}}"
USER_POOL_ID="${COGNITO_USER_POOL_ID}"

# Admin user details
ADMIN_EMAIL="${1:-admin@chartagent.local}"
ADMIN_PASSWORD="${2:-ChartAgent2024!}"
ADMIN_FIRST_NAME="System"
ADMIN_LAST_NAME="Administrator"

if [ -z "$USER_POOL_ID" ]; then
    echo "❌ Error: COGNITO_USER_POOL_ID not set"
    echo "   Run ./scripts/setup-cognito.sh first or set the environment variable"
    exit 1
fi

echo "👤 Creating admin user in Cognito..."
echo "   User Pool: $USER_POOL_ID"
echo "   Email: $ADMIN_EMAIL"

# Check if user exists
EXISTING_USER=$(aws cognito-idp admin-get-user \
    --user-pool-id $USER_POOL_ID \
    --username "$ADMIN_EMAIL" \
    --region $REGION \
    --query 'Username' \
    --output text 2>/dev/null || echo "")

if [ -n "$EXISTING_USER" ] && [ "$EXISTING_USER" != "None" ]; then
    echo "⚠️  User '$ADMIN_EMAIL' already exists"
    echo "   Updating attributes..."
    
    # Update user attributes
    aws cognito-idp admin-update-user-attributes \
        --user-pool-id $USER_POOL_ID \
        --username "$ADMIN_EMAIL" \
        --region $REGION \
        --user-attributes \
            'Name=given_name,Value='"$ADMIN_FIRST_NAME" \
            'Name=family_name,Value='"$ADMIN_LAST_NAME" \
            'Name=email_verified,Value=true' \
            'Name=custom:role,Value=admin' \
            'Name=custom:sources,Value=healthlake|epic|athena'
    
    echo "✅ User attributes updated"
else
    # Create user with temporary password
    aws cognito-idp admin-create-user \
        --user-pool-id $USER_POOL_ID \
        --username "$ADMIN_EMAIL" \
        --region $REGION \
        --temporary-password "$ADMIN_PASSWORD" \
        --user-attributes \
            'Name=email,Value='"$ADMIN_EMAIL" \
            'Name=email_verified,Value=true' \
            'Name=given_name,Value='"$ADMIN_FIRST_NAME" \
            'Name=family_name,Value='"$ADMIN_LAST_NAME" \
            'Name=custom:role,Value=admin' \
            'Name=custom:sources,Value=healthlake|epic|athena' \
        --message-action SUPPRESS
    
    echo "✅ User created with temporary password"
    
    # Set permanent password (skip force change password)
    aws cognito-idp admin-set-user-password \
        --user-pool-id $USER_POOL_ID \
        --username "$ADMIN_EMAIL" \
        --password "$ADMIN_PASSWORD" \
        --permanent \
        --region $REGION
    
    echo "✅ Permanent password set"
fi

# Add user to admins group
aws cognito-idp admin-add-user-to-group \
    --user-pool-id $USER_POOL_ID \
    --username "$ADMIN_EMAIL" \
    --group-name "admins" \
    --region $REGION 2>/dev/null || echo "   Already in admins group"

echo ""
echo "=============================================="
echo "✅ Admin user ready!"
echo "=============================================="
echo ""
echo "Login credentials:"
echo "   Email: $ADMIN_EMAIL"
echo "   Password: $ADMIN_PASSWORD"
echo ""

