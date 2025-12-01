# Chart Preparation Agent

AI-powered chart preparation system for healthcare providers using AWS HealthLake, Bedrock (Claude 3.5 Sonnet), and FHIR data.

## Quick Start

### Prerequisites
- AWS Account with admin access
- AWS CLI configured (`aws configure`)
- Docker installed
- Terraform installed
- Node.js 18+ and Python 3.11+

### Initial Setup

1. **Set up Terraform backend** (one-time):
```bash
./scripts/setup-terraform-backend.sh
```

2. **Create AWS HealthLake data store** (via AWS Console):
   - Go to AWS HealthLake console
   - Create a new FHIR R4 data store
   - Import Synthea synthetic data
   - Note the data store endpoint URL

3. **Enable AWS Bedrock**:
   - Go to AWS Bedrock console
   - Request access to Claude 3.5 Sonnet model
   - Wait for approval (usually instant)

4. **Configure environment**:
```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your HealthLake endpoint
```

### Daily Development (Local)

Start minimal AWS infrastructure and run locally:

```bash
# Start minimal AWS infrastructure
./scripts/start-dev.sh

# In one terminal - Backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# In another terminal - Frontend
cd frontend
npm install
npm start
```

Access at: `http://localhost:3000`

**Cost**: ~$0-5/month

### Weekly Integration Testing

Deploy full infrastructure to AWS ECS:

```bash
./scripts/start-testing.sh
```

Access via Application Load Balancer URL (shown in output)

**Cost**: ~$5-15/month (only while running)

### When Done Developing

Tear down all AWS infrastructure:

```bash
./scripts/teardown.sh
```

**Cost**: $0/month

## Architecture

- **Frontend**: React + TypeScript
- **Backend**: Python FastAPI
- **AI**: AWS Bedrock (Claude 3.5 Sonnet)
- **FHIR Data**: AWS HealthLake
- **Infrastructure**: AWS ECS/Fargate, VPC, ALB (managed by Terraform)

## Project Structure

```
Chart_Agent/
├── backend/           # Python FastAPI backend
├── frontend/          # React TypeScript frontend
├── terraform/         # Infrastructure as Code
├── scripts/           # Helper scripts
└── docs/             # Additional documentation
```

## Features

- **Patient List View**: Display provider's daily patient schedule
- **AI-Generated Summaries**: Automatic chart preparation using Claude
- **Conversational Q&A**: Ask follow-up questions about patient data
- **FHIR Integration**: Compatible with HealthLake and Epic FHIR
- **Cost-Optimized**: Pay only for what you use

## Documentation

- [Implementation Plan](PLAN.md) - Detailed implementation guide
- [AWS Setup Guide](docs/AWS_SETUP.md) - Step-by-step AWS configuration
- [Local Development](docs/LOCAL_DEV.md) - Running locally
- [Deployment Guide](docs/DEPLOYMENT.md) - Deploying to AWS

## Cost Management

| Environment | Monthly Cost |
|-------------|--------------|
| Local Development | $0-5 |
| Part-time Testing | $5-15 |
| Full Infrastructure | $100-150 |
| Everything Destroyed | $0 |

## Security & Compliance

- HIPAA-eligible AWS services
- IAM role-based authentication
- Encryption at rest and in transit
- CloudWatch audit logging
- VPC network isolation

## Support & Contribution

See [PLAN.md](PLAN.md) for detailed implementation phases and architecture decisions.

## License

Private - Healthcare Application

