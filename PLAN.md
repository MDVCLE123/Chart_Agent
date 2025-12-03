# Chart Preparation Agent - AWS-Native Implementation Plan

> **For Beginners**: This document provides detailed, step-by-step instructions for building a complete healthcare AI application. No prior experience needed! Follow along at your own pace.

## What You're Building

A web application that helps healthcare providers prepare for patient appointments by automatically summarizing patient records using AI. Think of it as an intelligent assistant that reads through medical records and creates a quick summary before a doctor's appointment.

## Architecture Overview

**Frontend**: React application for provider interface (the website doctors will use)  
**Backend**: Python (FastAPI) REST API on ECS/Fargate (the server that handles data)  
**AI**: AWS Bedrock with Claude 3.7 Sonnet for summarization (AI that reads and summarizes)  
**FHIR Data**: AWS HealthLake (database with patient medical records)  
**Infrastructure**: 100% AWS-native solution with containerized deployment  
**Data Sources**: HealthLake (dev/synthetic) → Epic sandbox → Production EHRs

### Simple Explanation
- **Frontend** = The website interface doctors see
- **Backend** = The behind-the-scenes server that processes requests
- **AI (Claude)** = Artificial intelligence that reads and summarizes medical data
- **FHIR** = Standard format for healthcare data (like how MP3 is a standard for music)
- **AWS** = Amazon Web Services - cloud platform hosting everything
- **Docker** = Packages your app so it runs the same everywhere
- **Pulumi** = Tool to create and manage AWS infrastructure with code

## Technical Stack

### Frontend
- React with TypeScript
- Axios for API calls
- Material-UI or Tailwind for healthcare-appropriate UI
- React Query for data fetching and caching

### Backend
- FastAPI (Python) for REST API
- `boto3` (AWS SDK) for all AWS service interactions
- `fhirclient` library for FHIR data operations (optional, can use boto3 directly)
- Pydantic for data validation
- Docker for containerization

### AWS Services (100% AWS-Native)
- **Amazon HealthLake**: FHIR R4 data store with synthetic patient data
- **Amazon Bedrock**: Claude 3.7 Sonnet for AI summarization and chat
- **ECS/Fargate**: Container orchestration (backend + frontend)
- **ECR**: Docker image registry
- **Application Load Balancer**: Route traffic to containers
- **Secrets Manager**: Store FHIR credentials and Epic API keys
- **IAM Roles**: Service authentication (no API keys for Bedrock!)
- **CloudWatch**: Logging and monitoring
- **VPC**: Network isolation and security
- **Cognito**: Provider authentication (optional)
- **Route 53**: DNS management (optional)

### FHIR Data Sources
1. **Development**: AWS HealthLake with Synthea synthetic data
2. **Testing**: Epic FHIR Sandbox
3. **Production**: Epic + other EHR FHIR APIs (via adapter pattern)

---

## Prerequisites (What You Need First)

### 1. Install Required Software

Before starting, install these tools on your computer:

**Essential Tools:**

1. **Code Editor - VS Code** (Recommended for beginners)
   - Download: https://code.visualstudio.com/
   - Why: Easy-to-use editor with helpful features for beginners
   - After installing, open VS Code and install these extensions:
     - Python
   - ESLint
   - Docker
   - HashiCorp Pulumi

2. **Git** (Version control)
   - Download: https://git-scm.com/
   - Why: Tracks changes to your code
   - Test it works: Open Terminal/Command Prompt and type: `git --version`

3. **Python 3.11+** (Backend programming language)
   - Download: https://www.python.org/downloads/
   - Why: The language your backend server uses
   - Test it works: `python3 --version` or `python --version`

4. **Node.js 18+** (Frontend tools)
   - Download: https://nodejs.org/ (get the LTS version)
   - Why: Needed to build the React website
   - Test it works: `node --version` and `npm --version`

5. **Docker Desktop** (Containerization)
   - Download: https://www.docker.com/products/docker-desktop
   - Why: Packages your app to run consistently everywhere
   - Test it works: `docker --version`

6. **Pulumi** (Infrastructure management)
   - macOS: `brew tap hashicorp/tap && brew install hashicorp/tap/pulumi`
   - Linux: Download from https://www.pulumi.io/downloads
   - Windows: `choco install pulumi`
   - Why: Creates AWS resources automatically
   - Test it works: `pulumi version`

7. **AWS CLI** (Amazon command line tool)
   - Download: https://aws.amazon.com/cli/
   - Why: Interact with Amazon Web Services
   - Test it works: `aws --version`

### 2. Create Accounts

**AWS Account** (Required)
1. Go to https://aws.amazon.com/
2. Click "Create an AWS Account"
3. Follow the signup process (credit card required, but you'll use free tier)
4. Enable MFA (multi-factor authentication) for security
5. Cost estimate: $5-15/month during development

**Why you need this:** AWS hosts your application in the cloud

### 3. Configure AWS CLI

After creating your AWS account:

```bash
# Run this command in Terminal/Command Prompt
aws configure

# You'll be asked for:
# - AWS Access Key ID: Get from AWS Console → Security Credentials
# - AWS Secret Access Key: Get from same place
# - Default region: Enter "us-east-1"
# - Default output format: Enter "json"
```

**Finding Your AWS Keys:**
1. Log into AWS Console: https://console.aws.amazon.com/
2. Click your name (top right) → Security Credentials
3. Scroll to "Access keys" → Create access key
4. Choose "Command Line Interface (CLI)"
5. Copy both keys and paste when running `aws configure`

---

## Implementation Phases

### Phase 1: AWS Setup & Project Structure

**Time Estimate**: 30-60 minutes  
**Difficulty**: Beginner-friendly (mostly clicking through AWS console)  
**What You'll Learn**: How to set up AWS services for healthcare data

**1.1 AWS HealthLake Setup**
- Create HealthLake data store (FHIR R4)
- Import AWS-provided Synthea synthetic dataset (sample patients)
- Note the HealthLake FHIR endpoint URL
- Configure IAM role with HealthLake read permissions
- Test FHIR API access with boto3

**1.2 AWS Bedrock Setup**
- Enable Amazon Bedrock in your AWS account (us-east-1 or us-west-2)
- Request access to Claude 3.7 Sonnet model (if not already enabled)
- Create IAM role with `bedrock:InvokeModel` permissions
- Test Bedrock API with sample prompts

**1.3 Clone and Set Up Project** (Detailed Steps)

Now let's get the code on your computer!

**Step-by-Step Instructions:**

1. **Open Terminal/Command Prompt**
   - **Mac**: Press Cmd+Space, type "Terminal", press Enter
   - **Windows**: Press Win+R, type "cmd", press Enter
   - **Linux**: Press Ctrl+Alt+T

2. **Navigate to Where You Want the Project**
   ```bash
   # Go to your Documents folder (or wherever you keep projects)
   cd Documents/Projects
   
   # If Projects folder doesn't exist, create it:
   mkdir -p Documents/Projects
   cd Documents/Projects
   ```

3. **Download This Project**
   ```bash
   # You're already in this project! Skip this step if you can see
   # the Chart_Agent folder. Otherwise, if starting fresh:
   git clone <your-repo-url> Chart_Agent
   cd Chart_Agent
   ```

4. **Verify Project Structure**
   ```bash
   # List files to confirm everything is there
   ls -la
   
   # You should see folders like:
   # - backend/
   # - frontend/
   # - pulumi/
   # - scripts/
   # - docs/
   ```

5. **Open Project in VS Code**
   ```bash
   # Open the project in VS Code
   code .
   
   # If 'code' command doesn't work:
   # - Open VS Code manually
   # - File → Open Folder
   # - Navigate to Chart_Agent folder
   # - Click "Open"
   ```

**What Just Happened?**
You now have all the code on your computer and can see it in VS Code. Think of this as getting all the building materials delivered to your construction site.

**Understanding the Project Structure**
```
Chart_Agent/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── healthlake_client.py # HealthLake/FHIR data fetching
│   │   ├── bedrock_service.py   # Bedrock Claude integration
│   │   ├── models.py            # Pydantic models
│   │   ├── config.py            # Configuration
│   │   └── utils.py             # Helper functions
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── PatientList.tsx
│   │   │   ├── PatientSummary.tsx
│   │   │   └── ChatInterface.tsx
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── App.tsx
│   │   └── config.ts
│   ├── Dockerfile
│   └── package.json
├── pulumi/                   # AWS infrastructure as code
│   ├── main.tf
│   ├── backend.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── dev.tfvars
│   ├── testing.tfvars
│   ├── vpc.tf
│   ├── nat.tf
│   ├── security_groups.tf
│   ├── iam.tf
│   ├── ecr.tf
│   ├── ecs.tf
│   ├── alb.tf
│   ├── healthlake.tf
│   └── cloudwatch.tf
├── scripts/                     # Helper scripts
│   ├── setup-pulumi-backend.sh
│   ├── start-dev.sh
│   ├── start-testing.sh
│   ├── teardown.sh
│   └── build-and-push.sh
├── docker-compose.yml           # Local development
└── README.md
```

---

**Each folder explained:**
- `backend/` - Python server code (the "brain" that processes data)
- `frontend/` - React website code (what users see in their browser)
- `pulumi/` - Infrastructure configuration (tells AWS what to create)
- `scripts/` - Helper commands (shortcuts to make your life easier)
- `docs/` - Documentation (guides like this one)

---

### Phase 2: Backend Development

**Time Estimate**: 1-2 hours  
**Difficulty**: Intermediate  
**What You'll Learn**: How to set up a Python web server that talks to AWS

**Overview**: The backend is already written for you! You just need to configure it with your AWS settings and run it.

**2.1 AWS HealthLake Integration**

Create `healthlake_client.py` to fetch FHIR resources:
- Patient demographics (Patient resource)
- Medical history (Condition resource)
- Recent encounters (Encounter resource)
- Lab results (Observation resource)
- Current medications (MedicationStatement/MedicationRequest)
- Allergies (AllergyIntolerance resource)
- Procedures (Procedure resource)

**Implementation approach**:
```python
import boto3
import requests
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

class HealthLakeClient:
    def __init__(self, datastore_endpoint):
        self.endpoint = datastore_endpoint
        self.session = boto3.Session()
        
    def search_patients(self, params):
        # Use FHIR search API with AWS SigV4 authentication
        # GET {endpoint}/Patient?_count=50
        pass
    
    def get_patient_data(self, patient_id):
        # Fetch all relevant resources for a patient
        # Bundle multiple FHIR API calls
        pass
```

**2.2 AWS Bedrock Integration**

Create `bedrock_service.py` for Claude AI:
```python
import boto3
import json

class BedrockService:
    def __init__(self):
        self.client = boto3.client('bedrock-runtime', region_name='us-east-1')
        self.model_id = 'anthropic.claude-3-7-sonnet-20250219-v1:0'
    
    def generate_summary(self, patient_data):
        # Format FHIR data into prompt
        # Call Bedrock with patient context
        # Return clinical summary
        pass
    
    def answer_question(self, question, patient_data, conversation_history):
        # Maintain conversation context
        # Use Claude for follow-up questions
        pass
```

**Key functions**:
1. **generate_summary()**: Send structured FHIR data to Claude via Bedrock
   - Prompt: "Summarize this patient's relevant history, recent visits, labs, and medications for an upcoming appointment"
   - Returns concise, clinically relevant summary
   
2. **answer_question()**: Enable conversational follow-ups
   - Maintains conversation context with patient data
   - Allows provider to ask specific questions

**2.3 FastAPI Endpoints**
```python
GET  /api/health                # Health check
GET  /api/patients              # List patients (from HealthLake)
GET  /api/patients/{id}         # Get patient FHIR data
POST /api/patients/{id}/summary # Generate Claude summary via Bedrock
POST /api/patients/{id}/chat    # Ask follow-up questions
```

**2.4 Environment Configuration**
- AWS region and HealthLake endpoint
- Bedrock model ID
- IAM role for ECS task (no hardcoded credentials!)
- CORS settings for React frontend

---

**2.5 Test Backend Locally** (Detailed Steps)

Let's make sure the backend works before moving on!

**Step-by-Step Instructions:**

1. **Create Python Virtual Environment**
   ```bash
   # Make sure you're in the backend folder
   cd backend
   
   # Create isolated Python environment
   python3 -m venv venv
   
   # Activate it:
   # Mac/Linux:
   source venv/bin/activate
   # Windows:
   venv\Scripts\activate
   
   # Your prompt should now show (venv)
   ```

2. **Install Python Dependencies**
   ```bash
   # Install all required Python packages
   pip install -r requirements.txt
   
   # This takes 1-2 minutes
   ```

3. **Start the Backend Server**
   ```bash
   # Start the development server
   uvicorn app.main:app --reload
   
   # You should see:
   # INFO: Uvicorn running on http://127.0.0.1:8000
   # INFO: Application startup complete
   ```

4. **Test in Browser**
   - Open your web browser
   - Go to: http://localhost:8000/docs
   - You should see interactive API documentation!
   - Try clicking on `/api/health` → "Try it out" → "Execute"
   - You should get a response showing the backend is healthy

5. **Keep This Running**
   - Leave this terminal window open
   - The backend needs to stay running
   - To stop it later: Press Ctrl+C

**What Just Happened?**
- **Virtual Environment**: Created an isolated space for Python packages (like a container for your project's dependencies)
- **Pip Install**: Downloaded all the code libraries the backend needs
- **Uvicorn**: Started a web server that listens for requests
- **API Docs**: Saw the interactive documentation showing all available endpoints

**Troubleshooting:**
- **Error about AWS credentials**: Make sure you ran `aws configure` earlier
- **Error about HealthLake**: Check your `.env` file has the correct endpoint URL
- **Port already in use**: Another program is using port 8000, try port 8001: `uvicorn app.main:app --reload --port 8001`

---

### Phase 3: Frontend Development

**Time Estimate**: 30-45 minutes  
**Difficulty**: Beginner  
**What You'll Learn**: How to run a React website that talks to your backend

**Overview**: The frontend (website) is already built! You just need to install dependencies and start it.

**3.1 Patient List Component**
- Display provider's patient list for the day
- Fetch from backend: `GET /api/patients`
- Show patient name, MRN, DOB, appointment time
- Click to select patient

**3.2 Patient Summary Component**
- Display patient demographics
- Show AI-generated summary from Bedrock/Claude
- Display key data sections organized by:
  - Active Conditions
  - Current Medications
  - Recent Labs (with abnormal flags)
  - Recent Visits
  - Allergies
- Loading states while fetching data
- Error handling for failed requests

**3.3 Chat Interface Component**
- Text input for provider questions
- Chat history display (conversational UI)
- Real-time responses from Claude via Bedrock
- Context-aware of current patient data
- Example questions suggested to user:
  - "What was the last A1C value?"
  - "Any recent medication changes?"
  - "Summarize cardiovascular history"

**3.4 Error Handling & UX**
- Loading indicators
- Error messages for failed API calls
- Empty states (no patients, no data)
- Responsive design for tablets/desktops
- Accessibility considerations (WCAG compliance)

---

---

### Phase 4: Containerization

**Time Estimate**: 20-30 minutes  
**Difficulty**: Intermediate  
**What You'll Learn**: How to package your app in Docker containers

**What is Containerization?**
Imagine you built a LEGO house. Containerization is like putting that house in a sealed box with instructions. Anyone can open the box and have the exact same house, regardless of where they are. Docker containers ensure your app runs the same way on any computer, anywhere.

**Why Do This?**
- Your app works the same on your computer, AWS, and your teammate's computer
- No more "it works on my machine" problems
- Easy to deploy to production

**Good News**: Docker files are already written for you! You just need to understand and test them.

**4.1 Backend Dockerfile**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./app/

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8000/api/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**4.2 Frontend Dockerfile**
```dockerfile
# Build stage
FROM node:18 AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

**4.3 Docker Compose (Local Development)**
- Backend container
- Frontend container
- Environment variables for local AWS credentials
- Volume mounts for hot reloading

---

---

### Phase 5: AWS Infrastructure & Deployment with Pulumi

**Time Estimate**: 1-2 hours (mostly waiting for AWS)  
**Difficulty**: Intermediate  
**What You'll Learn**: How to create AWS infrastructure automatically using code

**What is Infrastructure as Code (IaC)?**
Instead of clicking through AWS Console to create resources, you write configuration files that describe what you want. Pulumi reads these files and creates everything automatically. It's like having a robot assistant that sets up your AWS account exactly how you want it.

**Benefits:**
- ✅ Repeatable: Same setup every time
- ✅ Version controlled: Track changes in Git
- ✅ Destroyable: Delete everything with one command
- ✅ Cost-controlled: Only create what you need

**5.1 Pulumi Project Structure**

Create modular, reusable Pulumi configuration:
```
pulumi/
├── main.tf                    # Provider config, state backend
├── backend.tf                 # S3 state backend configuration
├── variables.tf               # Input variables
├── outputs.tf                 # Output values (ALB URL, etc.)
├── dev.tfvars                 # Dev environment (minimal cost)
├── testing.tfvars             # Testing environment (full stack)
├── production.tfvars          # Production environment
├── vpc.tf                     # VPC, subnets, routing
├── nat.tf                     # NAT Gateway (conditional)
├── security_groups.tf         # Security groups
├── iam.tf                     # IAM roles and policies
├── ecr.tf                     # Docker registries
├── ecs.tf                     # ECS cluster, services, tasks
├── alb.tf                     # Application Load Balancer
├── healthlake.tf              # HealthLake data store
├── cloudwatch.tf              # Log groups and monitoring
└── secrets.tf                 # Secrets Manager
```

**5.2 Cost-Aware Pulumi Configuration**

**variables.tf** - Control infrastructure costs:
```hcl
variable "enable_nat_gateway" {
  description = "Enable NAT Gateway (costs $32/month)"
  type        = bool
  default     = false  # Off by default for dev
}

variable "enable_alb" {
  description = "Enable Application Load Balancer"
  type        = bool
  default     = false  # Off by default, use local dev
}

variable "ecs_backend_count" {
  description = "Number of backend ECS tasks"
  type        = number
  default     = 0  # Off by default
}

variable "ecs_frontend_count" {
  description = "Number of frontend ECS tasks"
  type        = number
  default     = 0
}
```

**dev.tfvars** - Minimal cost configuration (~$0-5/month):
```hcl
environment              = "dev"
enable_nat_gateway       = false
enable_alb               = false
ecs_backend_count        = 0
ecs_frontend_count       = 0
healthlake_datastore_name = "chart-agent-dev"
```

**testing.tfvars** - Full infrastructure for testing:
```hcl
environment              = "testing"
enable_nat_gateway       = true
enable_alb               = true
ecs_backend_count        = 1
ecs_frontend_count       = 1
healthlake_datastore_name = "chart-agent-dev"
```

**5.3 Pulumi State Management**

**One-time setup** (before first `pulumi init`):
```bash
# Create S3 bucket for Pulumi state
aws s3 mb s3://chart-agent-pulumi-state
aws s3api put-bucket-versioning \
  --bucket chart-agent-pulumi-state \
  --versioning-configuration Status=Enabled

# Create DynamoDB table for state locking
aws dynamodb create-table \
  --table-name pulumi-state-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

**backend.tf** - Remote state configuration:
```hcl
pulumi {
  backend "s3" {
    bucket         = "chart-agent-pulumi-state"
    key            = "chart-agent/pulumi.tfstate"
    region         = "us-east-1"
    dynamodb_table = "pulumi-state-lock"
    encrypt        = true
  }
}
```

**5.4 Core Infrastructure Components**

**VPC & Networking** (vpc.tf):
- VPC with CIDR 10.0.0.0/16
- Public subnets (2 AZs) for ALB
- Private subnets (2 AZs) for ECS tasks
- Internet Gateway
- Route tables

**NAT Gateway** (nat.tf) - Conditional:
```hcl
resource "aws_nat_gateway" "main" {
  count = var.enable_nat_gateway ? 1 : 0
  
  allocation_id = aws_eip.nat[0].id
  subnet_id     = aws_subnet.public[0].id
  
  tags = {
    Name = "chart-agent-nat"
  }
}
```

**IAM Roles** (iam.tf):
```hcl
# ECS Task Role (for HealthLake + Bedrock)
resource "aws_iam_role" "ecs_task_role" {
  name = "chart-agent-ecs-task-role"
  
  inline_policy {
    name = "healthlake-bedrock-access"
    policy = jsonencode({
      Statement = [
        {
          Effect = "Allow"
          Action = [
            "healthlake:ReadResource",
            "healthlake:SearchWithGet",
            "healthlake:GetFHIRResource"
          ]
          Resource = "*"
        },
        {
          Effect = "Allow"
          Action = ["bedrock:InvokeModel"]
          Resource = "arn:aws:bedrock:*::foundation-model/anthropic.claude-*"
        }
      ]
    })
  }
}
```

**ECS Configuration** (ecs.tf):
- ECS cluster
- Task definitions (backend, frontend)
- ECS services with desired count from variables
- Auto-scaling policies (optional)

**Application Load Balancer** (alb.tf) - Conditional:
- ALB with HTTPS listener
- Target groups for backend/frontend
- Only created when `enable_alb = true`

**5.5 Helper Scripts for Infrastructure Management**

**scripts/setup-pulumi-backend.sh**:
```bash
#!/bin/bash
set -e
echo "Setting up Pulumi state backend..."
aws s3 mb s3://chart-agent-pulumi-state || true
aws s3api put-bucket-versioning \
  --bucket chart-agent-pulumi-state \
  --versioning-configuration Status=Enabled
aws dynamodb create-table \
  --table-name pulumi-state-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST || true
echo "✅ Pulumi backend ready!"
```

**scripts/start-dev.sh**:
```bash
#!/bin/bash
set -e
echo "Starting minimal dev infrastructure..."
cd pulumi
pulumi apply -var-file="dev.tfvars" -auto-approve
echo "✅ Dev infrastructure ready! Cost: ~$0-5/month"
echo "Run backend locally: cd backend && uvicorn app.main:app --reload"
echo "Run frontend locally: cd frontend && npm start"
```

**scripts/start-testing.sh**:
```bash
#!/bin/bash
set -e
echo "Starting full testing infrastructure..."
cd pulumi
pulumi apply -var-file="testing.tfvars" -auto-approve
./scripts/build-and-push.sh
ALB_DNS=$(pulumi output -raw alb_dns_name)
echo "✅ Testing infrastructure ready!"
echo "Access at: http://${ALB_DNS}"
```

**scripts/teardown.sh**:
```bash
#!/bin/bash
set -e
echo "⚠️  This will destroy ALL infrastructure!"
read -p "Are you sure? (yes/no): " confirm
if [ "$confirm" = "yes" ]; then
  cd pulumi
  pulumi destroy -auto-approve
  echo "✅ All resources deleted. Cost: $0/month"
else
  echo "Teardown cancelled"
fi
```

**scripts/build-and-push.sh**:
```bash
#!/bin/bash
set -e
AWS_REGION="us-east-1"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_BACKEND="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/chart-agent-backend"
ECR_FRONTEND="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/chart-agent-frontend"

aws ecr get-login-password --region ${AWS_REGION} | \
  docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

docker build -t chart-agent-backend ./backend
docker tag chart-agent-backend:latest ${ECR_BACKEND}:latest
docker push ${ECR_BACKEND}:latest

docker build -t chart-agent-frontend ./frontend
docker tag chart-agent-frontend:latest ${ECR_FRONTEND}:latest
docker push ${ECR_FRONTEND}:latest

echo "✅ Images pushed to ECR"
```

**5.6 Development Workflows**

**Local Development** (recommended for daily coding):
```bash
# Minimal AWS infrastructure (VPC, IAM, HealthLake)
./scripts/start-dev.sh

# Run backend/frontend locally
cd backend && uvicorn app.main:app --reload
cd frontend && npm start
```
**Cost**: $0-5/month (HealthLake storage + Bedrock usage only)

**Integration Testing** (weekly):
```bash
# Full infrastructure (ECS + ALB)
./scripts/start-testing.sh

# Test application
# ...

# Scale back to minimal
./scripts/start-dev.sh
```
**Cost**: Pay only for hours running ECS/ALB

**Extended Break** (vacation/hiatus):
```bash
./scripts/teardown.sh
```
**Cost**: $0/month

**5.7 Deployment Process**
1. Build Docker images locally
2. Tag and push to ECR (via build-and-push.sh)
3. Apply Pulumi to create/update infrastructure
4. ECS services automatically pull new images
5. Verify deployment via ALB endpoint or localhost

**5.8 Security & Compliance**
- HTTPS/TLS certificates (AWS Certificate Manager)
- Provider authentication via AWS Cognito (optional)
- HIPAA-compliant logging (CloudWatch with 7-year retention)
- Encryption at rest (HealthLake, S3) and in transit (TLS)
- IAM roles with least privilege (no hardcoded credentials)
- VPC private subnets for sensitive services
- Enable AWS Config for compliance tracking
- CloudTrail for audit logging
- Secrets Manager for Epic/EHR credentials

**5.9 Cost Monitoring & Optimization**

**Set up billing alerts**:
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name chart-agent-cost-alert \
  --metric-name EstimatedCharges \
  --namespace AWS/Billing \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 1
```

**Cost breakdown by scenario**:
- **Local Dev**: $0-5/month (HealthLake <10GB free + Bedrock usage)
- **Testing 4hrs/week**: $5-15/month (ECS/ALB part-time)
- **Full-time Dev**: $100-150/month (all services 24/7)
- **Destroyed**: $0/month (pulumi destroy)

**Best practice**: Use local development for daily coding, only spin up ECS/ALB for integration testing

---

### Phase 6: Epic FHIR Sandbox Integration

**6.1 Epic App Registration**
- Register application at fhir.epic.com
- Obtain client ID and credentials
- Configure OAuth2 flow (SMART on FHIR)
- Define scopes: `patient/*.read`, `launch`, `online_access`

**6.2 Multi-Source FHIR Adapter**

Create adapter pattern in backend to support multiple FHIR sources:
```python
class FHIRAdapter:
    @staticmethod
    def get_client(source='healthlake'):
        if source == 'healthlake':
            return HealthLakeClient()
        elif source == 'epic':
            return EpicFHIRClient()
        # Future: Cerner, Meditech, etc.

class EpicFHIRClient:
    def __init__(self):
        # Epic-specific OAuth2 authentication
        # Handle Epic FHIR API quirks
        pass
```

**6.3 Testing & Validation**
- Test data retrieval from Epic sandbox
- Verify OAuth2 SMART on FHIR flow
- Test Claude summarization with Epic data
- Compare Epic vs HealthLake data structures
- Document any Epic-specific handling needed

---

### Phase 7: Multi-EHR Compatibility

**7.1 Abstraction Layer**
- EHR adapter pattern supports different sources
- Handle different FHIR versions (R4 primarily, R3 fallback)
- Normalize data structures for Claude consumption
- Configuration-based EHR selection

**7.2 Configuration Management**
- Environment variables for EHR selection
- Secrets Manager for multi-EHR credentials
- Support multiple FHIR endpoints simultaneously

---

## Key Dependencies

**Python Backend** (requirements.txt):
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
boto3==1.34.0              # AWS SDK
pydantic==2.5.0
python-dotenv==1.0.0
httpx==0.25.0
fhirclient==4.1.0          # Optional, for FHIR convenience
python-jose==3.3.0         # JWT for authentication
```

**React Frontend** (package.json):
```
react==18.2.0
typescript==5.2.0
axios==1.6.0
@tanstack/react-query==5.8.0
@mui/material==5.14.0
@emotion/react==11.11.0
@emotion/styled==11.11.0
```

---

## FHIR Resources to Fetch

Priority resources for chart preparation:
1. **Patient** - Demographics, contact, identifiers
2. **Encounter** - Recent visits, admission/discharge dates
3. **Condition** - Active diagnoses, problem list, clinical status
4. **MedicationStatement** - Current active medications
5. **Observation** - Labs (A1C, glucose, lipids), vitals, assessments
6. **AllergyIntolerance** - Known allergies, severity
7. **Procedure** - Recent procedures, surgeries
8. **DocumentReference** - Clinical notes (if available)
9. **Immunization** - Vaccination history
10. **CarePlan** - Active care plans

---

## Claude/Bedrock Prompt Strategy

**Summary Prompt Template**:
```
You are a clinical AI assistant helping a healthcare provider prepare for a patient appointment. Provide a concise, clinically relevant summary.

PATIENT INFORMATION:
Name: {patient_name}
Age: {age} | Gender: {gender} | MRN: {mrn}

ACTIVE CONDITIONS:
{formatted_conditions}

RECENT VISITS (Last 6 months):
{formatted_encounters}

CURRENT MEDICATIONS:
{formatted_medications}

RECENT LABS:
{formatted_observations}

ALLERGIES:
{formatted_allergies}

RECENT PROCEDURES:
{formatted_procedures}

TASK: Provide a concise clinical summary highlighting:
1. Key active conditions requiring attention
2. Recent visit context and outcomes
3. Relevant lab findings (flag abnormal values)
4. Current medication regimen (note any high-risk meds)
5. Important safety considerations (allergies, drug interactions)

Format as bullet points for quick review before the appointment. Focus on actionable clinical information.
```

**Follow-up Chat System Prompt**:
```
You are a clinical AI assistant. The provider is reviewing patient {patient_name}. 
You have access to their complete medical record. Answer questions accurately and concisely.
Cite specific dates and values when relevant. If information is not in the record, say so clearly.
```

**Conversation Context**:
Maintain patient data in conversation history to enable questions like:
- "What was the patient's last A1C value?"
- "Any recent medication changes?"
- "Summarize cardiovascular history"
- "Are there any drug interactions to watch for?"

---

## Pulumi Infrastructure Management & Cost Optimization

### One-Command Infrastructure Control

**Setup Pulumi backend** (one-time):
```bash
./scripts/setup-pulumi-backend.sh
```

**Spin up minimal dev environment**:
```bash
cd pulumi
pulumi apply -var-file="dev.tfvars"
# Cost: ~$0-5/month
```

**Spin up full testing environment**:
```bash
pulumi apply -var-file="testing.tfvars"
# Cost: ~$50-70/month
```

**Tear down everything**:
```bash
pulumi destroy -auto-approve
# Cost: $0/month
```

### Cost Breakdown

| Scenario | Services Running | Monthly Cost |
|----------|------------------|--------------|
| **Local Dev** | HealthLake (<10GB) + Bedrock usage | $0-5 |
| **Testing 4hrs/week** | + ECS + ALB (part-time) | $5-15 |
| **Full-time Dev** | All services 24/7 | $100-150 |
| **Destroyed** | Nothing | $0 |

---

## Testing Strategy

1. **Unit Tests**: HealthLake client, Bedrock service functions
2. **Integration Tests**: End-to-end API flows with synthetic data
3. **Manual Testing**: UI/UX with HealthLake synthetic patients
4. **Epic Sandbox Testing**: Real-world EHR integration testing
5. **Performance Testing**: Response times for data fetch + summarization
6. **Security Testing**: IAM roles, authentication, data encryption
7. **Load Testing**: Simulate multiple concurrent providers

---

## Success Metrics

- Patient data retrieval from HealthLake: < 2 seconds
- Claude summary generation via Bedrock: < 5 seconds
- Total time from patient selection to summary display: < 8 seconds
- Support 50+ patients per provider daily
- 99%+ uptime (ECS health checks, ALB monitoring)
- Zero unauthorized data access (IAM audit)
- HIPAA-compliant audit logging (CloudWatch retention)

---

## Deployment Checklist

- [ ] AWS HealthLake data store created and populated
- [ ] Bedrock access enabled for Claude 3.7 Sonnet
- [ ] IAM roles configured with proper permissions
- [ ] Backend Docker image built and pushed to ECR
- [ ] Frontend Docker image built and pushed to ECR
- [ ] Pulumi infrastructure deployed (VPC, ECS, ALB)
- [ ] HTTPS certificate configured (Certificate Manager)
- [ ] CloudWatch dashboards set up
- [ ] Test with synthetic patients in HealthLake
- [ ] Epic sandbox integration tested
- [ ] Provider authentication configured (Cognito)
- [ ] Security review completed
- [ ] Documentation written

---

## Future Enhancements

- **Real-time Updates**: WebSocket for live patient data changes
- **Voice Interface**: Integrate Amazon Transcribe for voice questions
- **Mobile App**: React Native app with same backend
- **Predictive Analytics**: Amazon SageMaker for readmission risk
- **Care Gap Identification**: Analyze missing screenings/vaccinations
- **Multi-Provider Collaboration**: Shared notes and handoffs
- **EHR Write-Back**: Push summaries back to Epic (requires additional auth)
- **Additional EHRs**: Cerner, Meditech, Allscripts adapters
- **Multi-Language**: Support for non-English speaking providers
- **Offline Mode**: Cache data for unstable network environments

---

## Quick Start Guide

### Prerequisites
- AWS Account with admin access
- AWS CLI configured
- Docker installed
- Pulumi installed
- Node.js 18+ and Python 3.11+

### Initial Setup
1. Clone repository
2. Run `./scripts/setup-pulumi-backend.sh`
3. Create AWS HealthLake data store via AWS Console
4. Enable Bedrock access for Claude 3.7 Sonnet
5. Update `pulumi/dev.tfvars` with your HealthLake endpoint

### Daily Development
1. Start minimal AWS infrastructure: `./scripts/start-dev.sh`
2. Run backend: `cd backend && uvicorn app.main:app --reload`
3. Run frontend: `cd frontend && npm start`
4. Access at `http://localhost:3000`

### Weekly Testing
1. Deploy full stack: `./scripts/start-testing.sh`
2. Test via Application Load Balancer
3. Scale down: `./scripts/start-dev.sh`

### When Done
1. Tear down all resources: `./scripts/teardown.sh`
2. Confirm to delete all AWS infrastructure

---

**Last Updated**: December 2024  
**Version**: 1.0  
**Status**: Ready for Implementation

