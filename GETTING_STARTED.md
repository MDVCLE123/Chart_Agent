# Chart Preparation Agent - Getting Started Guide

> **AI-powered clinical chart preparation for healthcare providers**

A web application that helps doctors prepare for patient appointments by automatically summarizing medical records using Claude AI. Select a patient, click a button, and get an AI-generated summary in seconds.

---

## 🎯 Current Status

| Component | Status |
|-----------|--------|
| AWS Cognito Authentication | ✅ Working (50K MAUs free) |
| User Management | ✅ Working (Admin panel) |
| Role-Based Access Control | ✅ Working |
| Data Source Permissions | ✅ Working (Per-user) |
| AWS HealthLake | ✅ Working (48 Synthea patients) |
| AWS Bedrock (Claude Sonnet 4) | ✅ Working |
| Epic FHIR Sandbox | ✅ Working (7 test patients) |
| athenahealth Sandbox | ✅ Working (JWT auth) |
| Docker Development | ✅ Working |
| AI Summaries | ✅ Working |
| Follow-up Chat | ✅ Working |

---

## 🏗️ Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   React UI      │────▶│  FastAPI        │────▶│  FHIR Sources   │
│   (Material-UI) │     │  Backend        │     │                 │
│   Port 3000     │     │  Port 8000      │     │  • HealthLake   │
│   + Login       │     │  + Cognito Auth │     │  • Epic         │
│   + Settings    │     │  + User Mgmt    │     │  • athenahealth │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
        ┌─────────────────┐        ┌─────────────────┐
        │  AWS Cognito    │        │  AWS Bedrock    │
        │  User Pool      │        │  Claude Sonnet 4│
        └─────────────────┘        └─────────────────┘
```

**Tech Stack:**
- **Frontend**: React + TypeScript + Material-UI
- **Backend**: Python FastAPI
- **Authentication**: AWS Cognito (JWT tokens)
- **User Management**: Admin panel for user CRUD operations
- **AI**: AWS Bedrock (Claude Sonnet 4)
- **FHIR Auth**: JWT (RS384) for Epic & athenahealth, SigV4 for HealthLake
- **Container**: Docker Compose

---

## 📋 Prerequisites

Before starting, install:

- [ ] **Docker Desktop** - [Download](https://www.docker.com/products/docker-desktop)
- [ ] **AWS CLI** - [Download](https://aws.amazon.com/cli/)
- [ ] **AWS Account** with admin access

**Optional (for EHR sandbox testing):**
- [ ] Epic developer account at [fhir.epic.com](https://fhir.epic.com)
- [ ] athenahealth developer account at [developer.api.athena.io](https://developer.api.athena.io)

---

## 🚀 Quick Start (5 minutes)

### Step 1: Configure Environment

Create a `.env` file in the project root:

```bash
# AWS Configuration
AWS_REGION=us-east-2
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# Cognito Configuration (run ./scripts/setup-cognito.sh first)
USE_COGNITO=true
COGNITO_REGION=us-east-2
COGNITO_USER_POOL_ID=us-east-2_xxxxx
COGNITO_CLIENT_ID=xxxxx
COGNITO_CLIENT_SECRET=xxxxx

# HealthLake (get endpoint from AWS Console)
HEALTHLAKE_DATASTORE_ENDPOINT=https://healthlake.us-east-2.amazonaws.com/datastore/YOUR-ID/r4/

# Bedrock AI Model
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-20250514-v1:0

# Demo Mode (set false to use HealthLake)
USE_DEMO_MODE=false
```

### Step 2: Start with Docker

```bash
# Build and start all services
docker-compose up -d --build

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### Step 3: Set Up Cognito (First Time Only)

```bash
# Create Cognito User Pool and App Client
./scripts/setup-cognito.sh

# Create admin user
export COGNITO_USER_POOL_ID=us-east-2_xxxxx  # From script output
./scripts/create-cognito-admin.sh
```

**Default Admin Credentials:**
- **Email**: `admin@chartagent.local`
- **Password**: `ChartAgent2024!`

### Step 4: Open the App

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

### Step 5: Login and Test!

1. **Login** with admin credentials
2. Select a **Data Source** from the dropdown:
   - ☁️ **AWS HealthLake** - Your Synthea synthetic patients
   - 🏥 **Epic Sandbox** - 7 Epic test patients
   - 💚 **athenahealth Sandbox** - athenahealth test patients

3. Click a patient name
4. Click **"Generate Summary"**
5. Ask follow-up questions in the chat!

**Admin Features:**
- Click **Settings** (gear icon) to manage users
- Create users with specific data source permissions
- Link users to practitioners for auto-filtering

---

## 📁 Project Structure

```
Chart_Agent/
├── backend/                    # Python FastAPI
│   ├── app/
│   │   ├── main.py            # API endpoints
│   │   ├── cognito_auth.py    # AWS Cognito authentication
│   │   ├── healthlake_client.py  # Multi-source FHIR client
│   │   ├── bedrock_service.py    # Claude AI integration
│   │   ├── models.py          # Pydantic models
│   │   └── config.py          # Settings
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                   # React TypeScript
│   ├── src/
│   │   ├── components/
│   │   │   ├── LoginScreen.tsx    # Login UI
│   │   │   ├── SettingsPage.tsx   # Admin user management
│   │   │   ├── PatientList.tsx    # Patient list + source selector
│   │   │   ├── PatientSummary.tsx # Details + AI summary
│   │   │   └── ChatInterface.tsx  # Follow-up Q&A
│   │   ├── services/
│   │   │   ├── api.ts         # API client
│   │   │   └── auth.ts        # Authentication service
│   │   ├── context/
│   │   │   └── AuthContext.tsx    # Auth state management
│   │   └── types.ts           # TypeScript types
│   ├── Dockerfile
│   └── package.json
│
├── scripts/
│   ├── setup-cognito.sh       # Create Cognito User Pool
│   └── create-cognito-admin.sh # Create admin user
│
├── keys/                       # JWT keys (gitignored)
│   ├── epic_private_key.pem
│   └── jwks.json
│
├── docker-compose.yml          # Local development
├── .env                        # Environment variables (gitignored)
└── GETTING_STARTED.md          # This file
```

---

## 🔌 FHIR Data Sources

### AWS HealthLake (Your Data)
- Your own FHIR R4 data store with Synthea synthetic patients
- Authentication: AWS SigV4
- 48 patients with full medical history

### Epic Sandbox
- Epic's official FHIR test environment
- Authentication: JWT (RS384) with JWKS
- 7 test patients available:

| Patient | DOB | Gender |
|---------|-----|--------|
| Camila Maria Lopez | 1987-09-12 | Female |
| Derrick Lin | 1973-06-03 | Male |
| Desiree Caroline Powell | 2014-11-14 | Female |
| Elijah John Davis | 1993-08-18 | Male |
| Linda Jane Ross | 1969-04-27 | Female |
| Olivia Anne Roberts | 2003-01-07 | Female |
| Warren James McGinnis | 1952-05-24 | Male |

### athenahealth Sandbox
- athenahealth Preview API (FHIR R4)
- Authentication: JWT (RS384)
- Practice ID: 195900
- Test patients: Donna, Eleana, Frankie, Anna, Rebecca, Gary, Dorrie

---

## 🛠️ Development Workflow

### Daily Development

```bash
# Start services
docker-compose up -d

# Watch logs
docker-compose logs -f backend

# Rebuild after code changes
docker-compose up -d --build

# Stop services
docker-compose down
```

### Hot Reload

Backend code changes are automatically detected via volume mounts. Frontend requires rebuild:

```bash
docker-compose up -d --build frontend
```

### Common Commands

```bash
# Check service health
curl http://localhost:8000/api/health

# Test Epic patients
curl "http://localhost:8000/api/patients?fhir_source=epic"

# Test athenahealth patients
curl "http://localhost:8000/api/patients?fhir_source=athena"

# Generate summary
curl -X POST "http://localhost:8000/api/patients/{id}/summary?fhir_source=epic"
```

---

## 💰 Cost Estimates

| Mode | Services | Cost |
|------|----------|------|
| **Docker Dev** | HealthLake + Bedrock + Cognito | ~$1.50-2.00/day |
| **Stopped** | Nothing running | $0 |

**Breakdown:**
- HealthLake: ~$0.06/hour ($1.44/day)
- Bedrock (Claude Sonnet 4): ~$0.01-0.05 per summary
- **Cognito**: **FREE** for first 50,000 monthly active users! 🎉
- S3 (JWKS hosting): < $0.01/day

**💡 Tip**: Delete HealthLake datastore when not in use to save costs!

---

## 🔧 Troubleshooting

### Docker Issues

```bash
# Docker not running?
open -a Docker  # macOS

# Rebuild from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Backend Errors

```bash
# Check backend logs
docker-compose logs backend

# Verify AWS credentials
docker exec chart_agent-backend-1 python3 -c "from app.config import settings; print(settings.aws_region)"
```

### Frontend Not Updating

```bash
# Hard rebuild frontend
docker-compose build --no-cache frontend
docker-compose up -d frontend
# Then: Cmd+Shift+R in browser
```

### FHIR Source Errors

| Error | Solution |
|-------|----------|
| `InvalidClient` | Wait 15-30 min for OAuth propagation |
| `403 Forbidden` | Check IAM permissions for HealthLake |
| Empty patient list | Verify FHIR source is selected |

---

## 🔐 Security Notes

- **Never commit `.env` files** - They're gitignored
- **JWT keys in `/keys`** - Also gitignored
- **AWS credentials** - Use IAM roles in production
- **HIPAA compliance** - This is a development tool; production requires additional security

---

## 📚 API Endpoints

### Public Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |

### Authentication Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/login` | POST | Login with email/password |
| `/api/auth/me` | GET | Get current user info |
| `/api/auth/verify` | POST | Verify token validity |

### Protected Endpoints (Require Login)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/fhir-sources` | GET | List available FHIR sources |
| `/api/practitioners` | GET | List practitioners |
| `/api/patients` | GET | List patients |
| `/api/patients/{id}` | GET | Get patient details |
| `/api/patients/{id}/summary` | POST | Generate AI summary |
| `/api/patients/{id}/chat` | POST | Ask follow-up questions |

### Admin Endpoints (Admin Only)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/admin/users` | GET | List all users |
| `/api/admin/users` | POST | Create new user |
| `/api/admin/users/{username}` | PUT | Update user |
| `/api/admin/users/{username}` | DELETE | Delete user |

All patient/practitioner endpoints accept `?fhir_source=healthlake|epic|athena` query parameter. Users can only access their allowed data sources.

---

## 🚀 Next Steps

### Customize AI Prompts
Edit `backend/app/bedrock_service.py` to modify:
- Summary generation prompts
- Chat system prompts
- Clinical focus areas

### Add More FHIR Sources
The `healthlake_client.py` uses a factory pattern - add new sources by:
1. Adding to `FHIR_SOURCES` list
2. Implementing auth in `_make_request()`
3. Adding to frontend dropdown

### Deploy to AWS
```bash
# Setup Pulumi (one-time)
./scripts/setup-pulumi.sh

# Deploy infrastructure
./scripts/start-testing.sh

# Tear down when done
./scripts/teardown.sh
```

---

## 📖 Additional Resources

- [AWS HealthLake Docs](https://docs.aws.amazon.com/healthlake/)
- [Amazon Bedrock Docs](https://docs.aws.amazon.com/bedrock/)
- [Epic FHIR Documentation](https://fhir.epic.com/)
- [athenahealth API Docs](https://docs.athenahealth.com/)
- [FHIR R4 Specification](https://hl7.org/fhir/R4/)

---

## ✅ What's Working

- [x] AWS Cognito authentication (50K MAUs free)
- [x] User management (Create, Update, Delete)
- [x] Role-based access control (Admin/User)
- [x] Data source permissions (Per-user access)
- [x] Practitioner linking (Auto-filter)
- [x] AWS HealthLake with Synthea data
- [x] AWS Bedrock with Claude Sonnet 4
- [x] Epic FHIR Sandbox (JWT auth)
- [x] athenahealth Sandbox (JWT auth)
- [x] Multi-source FHIR client
- [x] AI-powered summaries
- [x] Follow-up chat
- [x] Docker development environment

---

**Last Updated**: December 2024  
**Version**: 2.2  

**New in v2.2:**
- 🔐 AWS Cognito authentication
- 👥 User management system
- 🔑 Role-based access control
- 📊 Data source permissions
- 👨‍⚕️ Practitioner linking

🎉 **Happy Coding!**
