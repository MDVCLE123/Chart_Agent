#!/bin/bash
# Setup Amazon Cognito User Pool for Chart Agent

set -e

# Configuration
REGION="${AWS_REGION:-us-east-2}"
POOL_NAME="chart-agent-users"
APP_CLIENT_NAME="chart-agent-app"

echo "🔐 Setting up Amazon Cognito for Chart Agent..."
echo "   Region: $REGION"

# Check if pool already exists
EXISTING_POOL=$(aws cognito-idp list-user-pools --max-results 60 --region $REGION \
    --query "UserPools[?Name=='$POOL_NAME'].Id" --output text 2>/dev/null || echo "")

if [ -n "$EXISTING_POOL" ] && [ "$EXISTING_POOL" != "None" ]; then
    echo "⚠️  User Pool '$POOL_NAME' already exists with ID: $EXISTING_POOL"
    USER_POOL_ID=$EXISTING_POOL
else
    echo "📦 Creating Cognito User Pool..."
    
    # Create User Pool with email as username and custom attributes
    USER_POOL_ID=$(aws cognito-idp create-user-pool \
        --pool-name "$POOL_NAME" \
        --region $REGION \
        --policies '{
            "PasswordPolicy": {
                "MinimumLength": 8,
                "RequireUppercase": true,
                "RequireLowercase": true,
                "RequireNumbers": true,
                "RequireSymbols": false,
                "TemporaryPasswordValidityDays": 7
            }
        }' \
        --auto-verified-attributes email \
        --username-attributes email \
        --username-configuration '{"CaseSensitive": false}' \
        --mfa-configuration OFF \
        --account-recovery-setting '{
            "RecoveryMechanisms": [
                {"Priority": 1, "Name": "verified_email"}
            ]
        }' \
        --schema '[
            {
                "Name": "email",
                "Required": true,
                "Mutable": true
            },
            {
                "Name": "name",
                "Required": false,
                "Mutable": true
            },
            {
                "Name": "role",
                "AttributeDataType": "String",
                "DeveloperOnlyAttribute": false,
                "Mutable": true,
                "Required": false,
                "StringAttributeConstraints": {
                    "MinLength": "1",
                    "MaxLength": "50"
                }
            },
            {
                "Name": "sources",
                "AttributeDataType": "String",
                "DeveloperOnlyAttribute": false,
                "Mutable": true,
                "Required": false,
                "StringAttributeConstraints": {
                    "MinLength": "1",
                    "MaxLength": "256"
                }
            },
            {
                "Name": "pract_id",
                "AttributeDataType": "String",
                "DeveloperOnlyAttribute": false,
                "Mutable": true,
                "Required": false,
                "StringAttributeConstraints": {
                    "MinLength": "0",
                    "MaxLength": "256"
                }
            },
            {
                "Name": "pract_name",
                "AttributeDataType": "String",
                "DeveloperOnlyAttribute": false,
                "Mutable": true,
                "Required": false,
                "StringAttributeConstraints": {
                    "MinLength": "0",
                    "MaxLength": "256"
                }
            }
        ]' \
        --admin-create-user-config '{
            "AllowAdminCreateUserOnly": false
        }' \
        --query 'UserPool.Id' \
        --output text)
    
    echo "✅ User Pool created: $USER_POOL_ID"
fi

# Check if app client exists
EXISTING_CLIENT=$(aws cognito-idp list-user-pool-clients --user-pool-id $USER_POOL_ID --region $REGION \
    --query "UserPoolClients[?ClientName=='$APP_CLIENT_NAME'].ClientId" --output text 2>/dev/null || echo "")

if [ -n "$EXISTING_CLIENT" ] && [ "$EXISTING_CLIENT" != "None" ]; then
    echo "⚠️  App Client '$APP_CLIENT_NAME' already exists with ID: $EXISTING_CLIENT"
    CLIENT_ID=$EXISTING_CLIENT
    
    # Get client secret
    CLIENT_SECRET=$(aws cognito-idp describe-user-pool-client \
        --user-pool-id $USER_POOL_ID \
        --client-id $CLIENT_ID \
        --region $REGION \
        --query 'UserPoolClient.ClientSecret' \
        --output text 2>/dev/null || echo "")
else
    echo "📱 Creating App Client..."
    
    # Create App Client (with secret for backend)
    CLIENT_RESULT=$(aws cognito-idp create-user-pool-client \
        --user-pool-id $USER_POOL_ID \
        --client-name "$APP_CLIENT_NAME" \
        --region $REGION \
        --generate-secret \
        --explicit-auth-flows \
            ALLOW_USER_PASSWORD_AUTH \
            ALLOW_ADMIN_USER_PASSWORD_AUTH \
            ALLOW_REFRESH_TOKEN_AUTH \
        --supported-identity-providers COGNITO \
        --prevent-user-existence-errors ENABLED \
        --access-token-validity 1 \
        --id-token-validity 1 \
        --refresh-token-validity 30 \
        --token-validity-units '{
            "AccessToken": "days",
            "IdToken": "days",
            "RefreshToken": "days"
        }' \
        --query 'UserPoolClient.[ClientId,ClientSecret]' \
        --output text)
    
    CLIENT_ID=$(echo $CLIENT_RESULT | awk '{print $1}')
    CLIENT_SECRET=$(echo $CLIENT_RESULT | awk '{print $2}')
    
    echo "✅ App Client created: $CLIENT_ID"
fi

# Create admin group if it doesn't exist
echo "👥 Setting up user groups..."
aws cognito-idp create-group \
    --user-pool-id $USER_POOL_ID \
    --group-name "admins" \
    --description "Administrator users with full access" \
    --region $REGION 2>/dev/null || echo "   Group 'admins' already exists"

aws cognito-idp create-group \
    --user-pool-id $USER_POOL_ID \
    --group-name "users" \
    --description "Regular users" \
    --region $REGION 2>/dev/null || echo "   Group 'users' already exists"

echo ""
echo "=============================================="
echo "✅ Cognito Setup Complete!"
echo "=============================================="
echo ""
echo "Add these to your .env file:"
echo ""
echo "COGNITO_USER_POOL_ID=$USER_POOL_ID"
echo "COGNITO_CLIENT_ID=$CLIENT_ID"
echo "COGNITO_CLIENT_SECRET=$CLIENT_SECRET"
echo "COGNITO_REGION=$REGION"
echo ""
echo "=============================================="

# Save to a file for easy reference
cat > /tmp/cognito-config.txt << EOF
# Cognito Configuration for Chart Agent
# Generated on $(date)

COGNITO_USER_POOL_ID=$USER_POOL_ID
COGNITO_CLIENT_ID=$CLIENT_ID
COGNITO_CLIENT_SECRET=$CLIENT_SECRET
COGNITO_REGION=$REGION
EOF

echo "📄 Configuration saved to /tmp/cognito-config.txt"
echo ""
echo "Next step: Run ./scripts/create-cognito-admin.sh to create the admin user"

