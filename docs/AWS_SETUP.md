# AWS Setup Guide

Complete guide to setting up AWS services for the Chart Preparation Agent.

## Prerequisites

- AWS Account with administrator access
- AWS CLI installed and configured
- Access to AWS Console

## Step 1: Configure AWS CLI

```bash
aws configure
```

Enter your:
- AWS Access Key ID
- AWS Secret Access Key
- Default region: `us-east-1` (recommended)
- Default output format: `json`

## Step 2: Create AWS HealthLake Data Store

### Via AWS Console

1. Navigate to [AWS HealthLake Console](https://console.aws.amazon.com/healthlake)
2. Click "Create data store"
3. Configure:
   - **Data store name**: `chart-agent-dev`
   - **FHIR version**: R4
   - **Preload data**: Select "Load sample data" (Synthea synthetic patients)
   - **KMS encryption**: Use default AWS managed key
4. Click "Create data store"
5. Wait for status to become "Active" (~5-10 minutes)
6. **Important**: Copy the "Data store endpoint URL" (needed for configuration)

### Via AWS CLI

```bash
aws healthlake create-fhir-datastore \
  --datastore-name chart-agent-dev \
  --datastore-type-version R4 \
  --preload-data-config PreloadDataType=SYNTHEA \
  --region us-east-1
```

Get the endpoint:
```bash
aws healthlake describe-fhir-datastore \
  --datastore-id <datastore-id> \
  --region us-east-1
```

## Step 3: Enable Amazon Bedrock

### Via AWS Console

1. Navigate to [Amazon Bedrock Console](https://console.aws.amazon.com/bedrock)
2. Click "Model access" in the left sidebar
3. Click "Request model access"
4. Find "Claude 3.7 Sonnet" by Anthropic
5. Check the box next to it
6. Click "Request model access"
7. Wait for approval (usually instant for Claude models)
8. Verify "Access granted" status

### Via AWS CLI

```bash
# Check available models
aws bedrock list-foundation-models \
  --region us-east-1 \
  --query "modelSummaries[?contains(modelId, 'claude')].{Name:modelName,ID:modelId}" \
  --output table

# Model ID to use: anthropic.claude-3-7-sonnet-20250219-v1:0
```

## Step 4: Create IAM Role for Development

Create a role for local development (or use your existing admin role):

```bash
# Create policy for HealthLake access
cat > healthlake-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "healthlake:ReadResource",
        "healthlake:SearchWithGet",
        "healthlake:GetFHIRResource",
        "healthlake:ListFHIRDatastores",
        "healthlake:DescribeFHIRDatastore"
      ],
      "Resource": "*"
    }
  ]
}
EOF

aws iam create-policy \
  --policy-name ChartAgentHealthLakeAccess \
  --policy-document file://healthlake-policy.json

# Create policy for Bedrock access
cat > bedrock-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:ListFoundationModels"
      ],
      "Resource": "*"
    }
  ]
}
EOF

aws iam create-policy \
  --policy-name ChartAgentBedrockAccess \
  --policy-document file://bedrock-policy.json
```

Attach these policies to your IAM user or role.

## Step 5: Test Access

### Test HealthLake Access

```bash
# List data stores
aws healthlake list-fhir-datastores --region us-east-1

# Describe your data store
aws healthlake describe-fhir-datastore \
  --datastore-id <your-datastore-id> \
  --region us-east-1
```

### Test Bedrock Access

```python
import boto3
import json

# Test Bedrock
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

response = bedrock.invoke_model(
    modelId='anthropic.claude-3-7-sonnet-20250219-v1:0',
    body=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 100,
        "messages": [
            {"role": "user", "content": "Say hello!"}
        ]
    })
)

result = json.loads(response['body'].read())
print(result['content'][0]['text'])
```

## Step 6: Configure Application

Update `backend/.env`:

```bash
AWS_REGION=us-east-1
HEALTHLAKE_DATASTORE_ENDPOINT=https://healthlake.us-east-1.amazonaws.com/datastore/<datastore-id>/r4/
BEDROCK_MODEL_ID=anthropic.claude-3-7-sonnet-20250219-v1:0
```

## Step 7: Set Up Billing Alerts (Recommended)

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name chart-agent-billing-alert \
  --alarm-description "Alert when charges exceed $10" \
  --metric-name EstimatedCharges \
  --namespace AWS/Billing \
  --statistic Maximum \
  --period 21600 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 1 \
  --alarm-actions <your-sns-topic-arn>
```

## Troubleshooting

### HealthLake Access Denied

**Error**: `AccessDeniedException` when accessing HealthLake

**Solution**: Ensure your IAM user/role has the HealthLake permissions listed above.

### Bedrock Model Not Available

**Error**: `ModelNotFound` or `AccessDeniedException`

**Solution**: 
1. Check that you've requested model access in the Bedrock console
2. Ensure you're using the correct region (us-east-1 or us-west-2)
3. Verify the model ID is correct

### HealthLake Data Store Taking Long to Create

**Normal**: Data store creation can take 5-15 minutes, especially with preloaded data.

**Check status**:
```bash
aws healthlake describe-fhir-datastore \
  --datastore-id <datastore-id> \
  --region us-east-1 \
  --query "DatastoreProperties.DatastoreStatus"
```

## Cost Tracking

Monitor your AWS costs:

```bash
# Check current month charges
aws ce get-cost-and-usage \
  --time-period Start=2024-12-01,End=2024-12-31 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=SERVICE
```

Or use [AWS Cost Explorer](https://console.aws.amazon.com/cost-management/home) in the console.

## Next Steps

Once AWS is configured:
1. Return to [README.md](../README.md) for local development setup
2. Configure `backend/.env` with your HealthLake endpoint
3. Run `./scripts/start-dev.sh` to deploy minimal infrastructure
4. Start coding!

## Resources

- [AWS HealthLake Documentation](https://docs.aws.amazon.com/healthlake/)
- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [FHIR R4 Specification](https://hl7.org/fhir/R4/)

