# Getting Started with Chart Preparation Agent

Quick guide to get your Chart Preparation Agent up and running in minutes.

## What You've Got

A complete, production-ready Chart Preparation Agent with:

- ✅ Python FastAPI backend with AWS HealthLake and Bedrock integration
- ✅ React TypeScript frontend with Material-UI
- ✅ Docker containerization for both services
- ✅ **Multi-source FHIR support**:
  - AWS HealthLake (your data)
  - Epic Sandbox (7 test patients) ✅ Working
  - athenahealth Sandbox (OAuth ready)
  - Demo/HAPI FHIR (public test data)
- ✅ Claude Sonnet 4 for AI summarization
- ✅ Complete Pulumi infrastructure for AWS deployment (Python!)
- ✅ Helper scripts for one-command deployment
- ✅ Cost-optimized configuration ($0-15/month for development)

## Prerequisites

Before you start, make sure you have:

- [ ] AWS Account with admin access
- [ ] AWS CLI installed and configured (`aws configure`)
- [ ] Pulumi CLI installed ([install guide](https://www.pulumi.com/docs/get-started/install/))
- [ ] Docker installed and running
- [ ] Node.js 18+ installed
- [ ] Python 3.11+ installed
- [ ] Git (for version control)

## 5-Minute Quick Start

### Step 1: AWS Setup (5 minutes)

```bash
# 1. Install and login to Pulumi
brew install pulumi  # macOS
pulumi login         # Use Pulumi Cloud (free) or --local

# 2. Setup Pulumi infrastructure
./scripts/setup-pulumi.sh

# 3. Follow the AWS Setup Guide to:
#    - Create HealthLake data store
#    - Enable Bedrock access
#    See: docs/AWS_SETUP.md
```

### Step 2: Configure Environment

```bash
# Create backend .env file
cp backend/.env.example backend/.env

# Edit backend/.env and add your HealthLake endpoint:
# HEALTHLAKE_DATASTORE_ENDPOINT=https://healthlake.us-east-1.amazonaws.com/datastore/YOUR-ID/r4/
```

### Step 3: Run Locally with Docker (Recommended)

```bash
# Create .env file in project root with your credentials:
cat > .env << 'EOF'
AWS_REGION=us-east-2
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
HEALTHLAKE_DATASTORE_ENDPOINT=https://healthlake.us-east-2.amazonaws.com/datastore/YOUR-ID/r4/
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-20250514-v1:0
USE_DEMO_MODE=false
EOF

# Start with Docker Compose
docker-compose up -d --build

# View logs
docker-compose logs -f
```

**Access**: 
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs

**Cost**: ~$0-5/month

### Step 4: Test with Real Data

1. Open http://localhost:3000
2. **Select a FHIR Source** from the dropdown:
   - **AWS HealthLake**: Your Synthea synthetic patients
   - **Epic Sandbox**: 7 real Epic test patients (Camila Lopez, Derrick Lin, etc.)
   - **Public FHIR Server**: Demo data from HAPI FHIR
3. Click a patient to view their details
4. Click "Generate Summary" to see Claude Sonnet 4 in action
5. Try asking questions in the chat interface:
   - "What medications is this patient on?"
   - "Summarize recent lab results"
   - "Any allergies I should know about?"

## Alternative: Deploy to AWS (Full Stack)

For integration testing or demo purposes:

```bash
# Deploy complete infrastructure to AWS
./scripts/start-testing.sh

# Access via ALB URL (shown in output)
# Cost: ~$50-70/month while running
```

When done testing:

```bash
# Scale back to minimal infrastructure
./scripts/start-dev.sh

# Or tear down everything
./scripts/teardown.sh
```

## Project Structure

```
Chart_Agent/
├── backend/              # Python FastAPI backend
│   ├── app/
│   │   ├── main.py              # FastAPI application & endpoints
│   │   ├── healthlake_client.py # Multi-source FHIR client
│   │   │                        # (HealthLake, Epic, athenahealth, Demo)
│   │   ├── bedrock_service.py   # Claude Sonnet 4 integration
│   │   ├── models.py            # Pydantic data models
│   │   └── config.py            # Configuration settings
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/             # React TypeScript frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── PatientList.tsx      # Patient list with FHIR source dropdown
│   │   │   ├── PatientSummary.tsx   # Patient details & AI summary
│   │   │   └── ChatInterface.tsx    # Follow-up questions
│   │   ├── services/api.ts          # API client with FHIR source param
│   │   └── App.tsx                  # Main app
│   ├── Dockerfile
│   └── package.json
│
├── keys/                 # Epic JWT keys (gitignored)
│   ├── epic_private_key.pem
│   ├── epic_public_key.pem
│   └── jwks.json
│
├── infrastructure/       # Pulumi Infrastructure (Python)
│   ├── __main__.py              # Infrastructure code
│   ├── Pulumi.yaml              # Project definition
│   ├── Pulumi.dev.yaml          # Dev config (minimal cost)
│   └── Pulumi.testing.yaml      # Test config (full stack)
│
├── scripts/              # Helper scripts
│   ├── setup-pulumi.sh
│   ├── start-dev.sh
│   ├── start-testing.sh
│   ├── teardown.sh
│   └── build-and-push.sh
│
├── docker-compose.yml    # Local development with Docker
├── .env                  # Environment variables (gitignored)
│
└── docs/                 # Documentation
    ├── AWS_SETUP.md
    └── EPIC_INTEGRATION.md
```

## Development Workflow

### Daily Development with Docker

```bash
# Start all services
docker-compose up -d

# Watch logs
docker-compose logs -f

# Rebuild after code changes
docker-compose up -d --build

# Stop services
docker-compose down
```

**Hot reload enabled**: Backend code changes automatically reflect via volume mounts

### Weekly Testing

```bash
# Deploy to AWS for integration testing
./scripts/start-testing.sh

# Test, then scale back
./scripts/start-dev.sh
```

### When Not Developing

```bash
# Destroy everything to save costs
./scripts/teardown.sh
```

## Common Tasks

### Update Dependencies

```bash
# Backend
cd backend
pip install --upgrade -r requirements.txt

# Frontend
cd frontend
npm update
```

### Build Docker Images

```bash
# Build and push to AWS ECR
./scripts/build-and-push.sh
```

### Deploy Updates to ECS

```bash
# Deploy new images to running ECS services
./scripts/deploy.sh
```

### View Logs

```bash
# Backend logs (if running in ECS)
aws logs tail /ecs/chart-agent-backend-dev --follow

# Frontend logs
aws logs tail /ecs/chart-agent-frontend-dev --follow
```

### Check Costs

```bash
# View current month AWS costs
aws ce get-cost-and-usage \
  --time-period Start=2024-12-01,End=2024-12-31 \
  --granularity MONTHLY \
  --metrics BlendedCost
```

## Next Steps

### 1. Customize for Your Use Case

- Modify `backend/app/bedrock_service.py` to adjust AI prompts
- Update `frontend/src/components/` to change UI/UX
- Add additional FHIR resources as needed

### 2. Integrate with Epic

Follow [docs/EPIC_INTEGRATION.md](docs/EPIC_INTEGRATION.md) to:
- Register app with Epic
- Test with Epic sandbox
- Switch data source from HealthLake to Epic

### 3. Add Authentication

Integrate AWS Cognito for provider authentication:

```bash
# See: https://docs.aws.amazon.com/cognito/
# Update frontend to use Cognito auth
# Update backend to validate Cognito tokens
```

### 4. Production Deployment

- Set up CI/CD pipeline (GitHub Actions recommended)
- Configure HTTPS with ACM certificates
- Set up CloudWatch alarms and dashboards
- Enable AWS Config for compliance
- Review security settings

### 5. Monitoring & Observability

```bash
# Set up CloudWatch dashboards
# Configure alerts for errors and high costs
# Enable X-Ray tracing for debugging
```

## Troubleshooting

### Backend won't start

**Check**:
- Is HealthLake endpoint correct in `.env`?
- Are AWS credentials configured?
- Is Python 3.11+ installed?

### Frontend can't reach backend

**Check**:
- Is backend running on port 8000?
- Check CORS settings in `backend/app/main.py`
- Check `REACT_APP_API_URL` in frontend

### Can't access HealthLake

**Check**:
- Is HealthLake data store created and active?
- Are IAM permissions correct?
- Is the endpoint URL correct?

### Bedrock not working

**Check**:
- Is Bedrock enabled in your AWS account?
- Have you requested access to Claude models?
- Is the model ID correct?

### Pulumi errors

**Check**:
- Are AWS credentials valid? Run `aws sts get-caller-identity`
- Check Pulumi stack status: `pulumi stack --show-urns`
- View stack outputs: `pulumi stack output`
- Check Pulumi logs: `pulumi logs`

## Support & Resources

### Documentation

- [README.md](README.md) - Project overview
- [PLAN.md](PLAN.md) - Detailed implementation plan
- [docs/AWS_SETUP.md](docs/AWS_SETUP.md) - AWS configuration guide
- [docs/EPIC_INTEGRATION.md](docs/EPIC_INTEGRATION.md) - Epic integration guide

### External Resources

- [AWS HealthLake Docs](https://docs.aws.amazon.com/healthlake/)
- [Amazon Bedrock Docs](https://docs.aws.amazon.com/bedrock/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Pulumi Documentation](https://www.pulumi.com/docs/)
- [Pulumi AWS Guide](https://www.pulumi.com/docs/clouds/aws/get-started/)
- [Pulumi Python](https://www.pulumi.com/docs/languages-sdks/python/)

## Cost Summary

| Mode | Services | Monthly Cost |
|------|----------|--------------|
| **Docker Dev** (Recommended) | HealthLake + Bedrock usage only | ~$45-60 |
| **Part-time Testing** | + ECS + ALB (4 hours/week) | $60-80 |
| **Full-time Running** | All services 24/7 | $100-150 |
| **Destroyed** | Nothing | $0 |

**Daily Cost Breakdown**:
- HealthLake: ~$1.44/day ($0.06/hour)
- Bedrock (Claude Sonnet 4): ~$0.01-0.05 per summary
- S3 (JWKS hosting): < $0.01/day

**Tip**: Delete HealthLake datastore when not in use to save costs!

## You're Ready! 🚀

Start with local development for fast iteration, then deploy to AWS when you need integration testing. The infrastructure is designed to be cost-effective and easy to tear down when not in use.

Questions? Check the documentation in `/docs` or review the implementation plan in `PLAN.md`.

**Happy Coding!**

