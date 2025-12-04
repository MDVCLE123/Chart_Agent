# Chart Preparation Agent - Complete Beginner's Guide

> **Welcome!** This guide assumes you're brand new to development. We'll walk through everything step-by-step, explaining technical terms as we go.

## 📚 Table of Contents

1. [What You're Building](#what-youre-building)
2. [Prerequisites - What to Install](#prerequisites)
3. [Phase 1: AWS Setup](#phase-1-aws-setup)
4. [Phase 2: Running Locally with Docker](#phase-2-running-locally-with-docker)
5. [Phase 3: Understanding the Code](#phase-3-understanding-the-code)
6. [Phase 4: FHIR Data Sources](#phase-4-fhir-data-sources) (All 3 working!)
7. [Phase 5: Deploying to AWS](#phase-5-deploying-to-aws)
8. [Troubleshooting](#troubleshooting)
9. [Next Steps](#next-steps)
10. [Current Project Status](#current-project-status)

---

## What You're Building

**Chart Preparation Agent** helps doctors prepare for appointments by:
- Showing a list of today's patients
- Automatically summarizing each patient's medical history using AI
- Allowing doctors to ask questions about patient data

**Real-world example**: A doctor has 20 patients today. Instead of reading through hundreds of pages of medical records, they click a button and get a 1-page AI summary for each patient.

### Technical Components (Explained Simply)

- **Frontend** = Website that doctors see in their browser
- **Backend** = Server that processes requests (like a restaurant kitchen)
- **FHIR Data Sources** = Where patient data comes from:
  - ☁️ AWS HealthLake (your own data store - 48 patients)
  - 🏥 Epic Sandbox (7 test patients)
  - 💚 athenahealth Sandbox (7 test patients)
- **AI** = Claude Sonnet 4 reads medical records and creates summaries
- **Cloud** = AWS hosts everything so it works from anywhere
- **Docker** = Packages your app so it runs the same everywhere
- **JWT** = JSON Web Tokens for secure authentication with Epic & athenahealth

---

## Prerequisites

### Step 1: Install Software (30-45 minutes)

Install these tools in order. After each one, verify it works with the test command.

#### 1. VS Code (Code Editor)

**What it is**: Like Microsoft Word, but for code  
**Download**: https://code.visualstudio.com/

**After installing:**
1. Open VS Code
2. Go to Extensions (sidebar icon that looks like blocks)
3. Install these extensions:
   - Python (required for Pulumi!)
   - Pylance (Python language server)
   - ESLint  
   - Docker

**Test it works**: You should be able to open VS Code

---

#### 2. Git (Version Control)

**What it is**: Tracks changes to your code (like "track changes" in Word)  
**Download**: https://git-scm.com/

**After installing, test it:**
```bash
git --version
# Should show: git version 2.x.x
```

**Configure Git** (one-time setup):
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

---

#### 3. Python 3.11+ (Programming Language)

**What it is**: Language the backend is written in  
**Download**: https://www.python.org/downloads/

**After installing, test it:**
```bash
python3 --version
# Should show: Python 3.11.x or higher
```

**If `python3` doesn't work, try `python`:**
```bash
python --version
```

---

#### 4. Node.js 18+ (JavaScript Runtime)

**What it is**: Needed to build the React frontend  
**Download**: https://nodejs.org/ (get the LTS version)

**After installing, test both:**
```bash
node --version
# Should show: v18.x.x or higher

npm --version
# Should show: 9.x.x or higher
```

---

#### 5. Docker Desktop (Containerization)

**What it is**: Packages your app so it runs the same everywhere  
**Download**: https://www.docker.com/products/docker-desktop

**After installing:**
1. Start Docker Desktop application
2. Wait for it to say "Docker Desktop is running" (green)

**Test it works:**
```bash
docker --version
# Should show: Docker version 24.x.x
```

---

#### 6. Pulumi (Infrastructure Tool)

**What it is**: Modern Infrastructure as Code using REAL PYTHON CODE (not YAML!)  
**Why Pulumi?**: Write infrastructure using actual programming languages

**Install:**

**macOS:**
```bash
brew install pulumi
```

**Linux:**
```bash
curl -fsSL https://get.pulumi.com | sh
```

**Windows:**
```powershell
choco install pulumi
```

**Test it works:**
```bash
pulumi version
# Should show: v3.x.x
```

**Benefits:**
- ✅ Use Python (or TypeScript, Go, C#, Java)
- ✅ Full IDE support (autocomplete, type checking)
- ✅ Real programming (loops, conditionals, functions)
- ✅ Multi-cloud support (AWS, Azure, GCP, Kubernetes)
- ✅ Free for individuals (Pulumi Cloud)
- ✅ Better error messages than YAML configs

---

#### 7. AWS CLI (Amazon Command Line Tool)

**What it is**: Lets you control AWS from your terminal  
**Download**: https://aws.amazon.com/cli/

**Test it works:**
```bash
aws --version
# Should show: aws-cli/2.x.x
```

---

### Step 2: Create AWS Account (15 minutes)

**Cost Warning**: AWS isn't free, but during development you'll spend $5-15/month

**Steps:**
1. Go to https://aws.amazon.com/
2. Click "Create an AWS Account"
3. Fill in:
   - Email address
   - Password
   - Account name
4. Enter credit card information (required even for free tier)
5. Verify your identity (phone verification)
6. Choose "Free" support plan
7. Wait for account activation email (1-2 minutes)

**Enable MFA (Highly Recommended):**
1. Log into AWS Console
2. Click your name (top right) → Security Credentials
3. Under "Multi-factor authentication (MFA)" → Assign MFA device
4. Use Google Authenticator or similar app

---

### Step 3: Configure AWS CLI (5 minutes)

Now let's connect the AWS CLI to your account.

**Get Your AWS Keys:**
1. Log into AWS Console: https://console.aws.amazon.com/
2. Click your name (top right) → Security Credentials
3. Scroll to "Access keys"
4. Click "Create access key"
5. Choose "Command Line Interface (CLI)"
6. Check "I understand" and click Next
7. Copy both:
   - Access Key ID (starts with AKIA...)
   - Secret Access Key (long random string)

**Configure CLI:**
```bash
aws configure
```

**Enter when prompted:**
```
AWS Access Key ID: (paste your key)
AWS Secret Access Key: (paste your secret)
Default region name: us-east-1
Default output format: json
```

**Test it works:**
```bash
aws sts get-caller-identity
```

You should see your account ID and user info.

---

## Phase 1: AWS Setup

### 1.1 Create HealthLake Data Store (15 minutes)

HealthLake stores patient medical records in FHIR format.

**Steps:**

1. **Go to HealthLake**
   - Open AWS Console
   - Search for "HealthLake" in top search bar
   - Click "AWS HealthLake"

2. **Create Data Store**
   - Click orange "Create data store" button
   - Fill in:
     - **Name**: `chart-agent-dev`
     - **FHIR version**: R4
     - **Preload data**: ✅ Check "Load sample data"
     - **Sample data type**: Synthea
   - Click "Create data store"

3. **Wait for Creation** (5-10 minutes)
   - Status shows "Creating..."
   - Refresh page every minute
   - When status is "Active", you're done!

4. **Copy Endpoint URL**
   - Click on `chart-agent-dev`
   - Find "Data store endpoint URL"
   - It looks like: `https://healthlake.us-east-1.amazonaws.com/datastore/abc123def456.../r4/`
   - **IMPORTANT**: Copy this entire URL
   - Paste it into a notepad - you'll need it soon!

**What you just did**: Created a database filled with fake patient records for testing.

---

### 1.2 Enable Bedrock AI (10-15 minutes)

Bedrock gives you access to Claude AI for summarizing text.

**Steps:**

1. **Go to Bedrock**
   - AWS Console search bar → "Bedrock"
   - Click "Amazon Bedrock"

2. **Go to Model Catalog**
   - Left sidebar → "Model catalog"
   - Find "Anthropic" section
   - Click on "Claude Sonnet 4" (recommended) or "Claude 3.7 Sonnet"

3. **Submit Use Case Details** (Required for first-time users)
   - You'll see a yellow banner: "Anthropic requires first-time customers to submit use case details"
   - Click **"Submit use case details"** button
   - Fill out the form:

   | Field | What to Enter |
   |-------|---------------|
   | **Company name** | Your company or organization name |
   | **Company website URL** | Your company website or LinkedIn profile |
   | **Industry** | Select "Healthcare" |
   | **Intended users** | ✅ Check "Internal users (employees, staff, team members)" |
   | **Use case description** | See example below |

   **Example use case description** (copy and modify):
   ```
   Building a clinical decision support tool for healthcare providers. 
   The application retrieves patient data from FHIR-compliant electronic 
   health records and generates pre-appointment summaries of relevant 
   medical history, recent visits, lab results, and medications. 
   Providers can also ask follow-up questions about patient data.
   ```

   ⚠️ **Important**: Do NOT mention "Claude" in your description - it will be auto-denied!

   - Click **"Submit use case details"**

4. **Request Model Access**
   - Left sidebar → "Model access"
   - Click "Manage model access" (top right)
   - Find "Anthropic" section
   - ✅ Check "Claude Sonnet 4" (recommended)
   - ✅ Check "Claude 3 Haiku" (optional, cheaper for testing)
   - Scroll down, click "Request model access"

5. **Wait for Approval** (Usually instant to a few hours)
   - Refresh the page
   - Should see green "Access granted" next to Claude models
   - If "Pending", wait and refresh periodically

**Model ID for Configuration**: `us.anthropic.claude-sonnet-4-20250514-v1:0`

**What you just did**: Got permission to use Claude AI, which will read and summarize medical records.

---

### 1.3 Get the Code (5 minutes)

**You already have the code!** You're reading this file, which means you have the Chart_Agent folder.

**Verify you have everything:**
```bash
# Navigate to the project
cd /path/to/Chart_Agent

# List contents
ls -la

# You should see:
# - backend/
# - frontend/
# - infrastructure/
# - scripts/
# - docs/
# - GETTING_STARTED.md (full guide)
# - README.md
```

**Open in VS Code:**
```bash
# From the Chart_Agent folder:
code .
```

VS Code should open with all your project files visible in the sidebar.

---

## Phase 2: Running Locally with Docker

Now let's get the application running on your computer using Docker!

### 2.1 Configure Environment (10 minutes)

**Create the root `.env` configuration file:**

1. In VS Code, right-click on the project root folder (Chart_Agent)
2. Select "New File"
3. Name it `.env` (include the dot!)
4. Paste the following content:

```bash
# AWS Configuration
AWS_REGION=us-east-2
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key

# HealthLake Configuration - REPLACE WITH YOUR DATASTORE ID
HEALTHLAKE_DATASTORE_ENDPOINT=https://healthlake.us-east-2.amazonaws.com/datastore/YOUR-DATASTORE-ID/r4/

# Bedrock Configuration (Claude Sonnet 4)
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-20250514-v1:0

# Demo Mode (set to false to use HealthLake)
USE_DEMO_MODE=false

# athenahealth Configuration (optional)
ATHENA_CLIENT_ID=your-athena-client-id
ATHENA_CLIENT_SECRET=your-athena-client-secret
```

5. **Important**: Replace placeholders with your actual values
6. Save the file (Cmd+S or Ctrl+S)

**💡 Tip**: If you don't see the `.env` file after creating it, VS Code might be hiding dotfiles. Click the refresh icon in the Explorer panel.

---

### 2.2 Start with Docker Compose (5 minutes)

**Make sure Docker Desktop is running!**

**Open Terminal in VS Code:**
- Menu: Terminal → New Terminal
- Or press: Ctrl+` (backtick key)

**Run these commands:**
```bash
# Make sure you're in the project root folder
cd /path/to/Chart_Agent

# Build and start all services
docker-compose up -d --build

# Watch the logs
docker-compose logs -f
```

**Success looks like:**
```
chart_agent-backend-1   | INFO:     Uvicorn running on http://0.0.0.0:8000
chart_agent-backend-1   | INFO:     Application startup complete.
chart_agent-frontend-1  | nginx is running...
```

**Test it:**
- Backend API: http://localhost:8000/docs
- Frontend App: http://localhost:3000

---

### 2.3 Docker Commands Cheat Sheet

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build

# View logs
docker-compose logs -f

# Restart backend only
docker restart chart_agent-backend-1

# Check running containers
docker ps
```

---

### 2.4 Use the Application! 🎉

You should now see:
- **Top**: Data Source dropdown with 3 options
- **Left side**: List of patients
- **Right side**: Patient details and AI summary

**Try it out:**
1. **Select a Data Source** from the dropdown:
   - ☁️ **AWS HealthLake**: Your Synthea synthetic patients (48 patients)
   - 🏥 **Epic Sandbox**: 7 real Epic test patients
   - 💚 **athenahealth Sandbox**: 7 athenahealth test patients
2. Click on a patient name
3. You'll see their demographics
4. Click **"Generate Summary"** button
5. Wait 5-10 seconds
6. **AI-generated summary appears!**
7. Try asking questions in the chat box:
   - "What was the patient's last A1C value?"
   - "Any recent medication changes?"
   - "Summarize cardiovascular history"

**Congratulations!** You're running a full healthcare AI application on your computer!

---

## Phase 4: FHIR Data Sources

Your app supports 3 FHIR data sources (all working!):

### 4.1 AWS HealthLake (Your Data)

Your own FHIR data store with Synthea synthetic patients (48 patients).
- **Authentication**: AWS SigV4
- **Data**: Full medical history including conditions, medications, labs, encounters

**Status**: ✅ Working

### 4.2 Epic Sandbox (7 Test Patients)

Epic's official FHIR test environment.
- **Authentication**: JWT (RS384) with JWKS hosted on S3
- **Client ID**: `5f2384c3-5bb4-484f-a528-068177894d81`

**Test Patients Available**:
| Patient | DOB | Gender |
|---------|-----|--------|
| Camila Maria Lopez | 1987-09-12 | Female |
| Derrick Lin | 1973-06-03 | Male |
| Desiree Caroline Powell | 2014-11-14 | Female |
| Elijah John Davis | 1993-08-18 | Male |
| Linda Jane Ross | 1969-04-27 | Female |
| Olivia Anne Roberts | 2003-01-07 | Female |
| Warren James McGinnis | 1952-05-24 | Male |

**Status**: ✅ Working

### 4.3 athenahealth Sandbox (7 Test Patients)

athenahealth Preview API (FHIR R4).
- **Authentication**: JWT (RS384) - same key as Epic!
- **Client ID**: `0oa104juaipwtISjQ298`
- **Practice ID**: 195900

**Test Patients Available**:
| Patient | Last Name |
|---------|-----------|
| Donna | Sandboxtest |
| Eleana | Sandboxtest |
| Frankie | Sandboxtest |
| Anna | Sandbox-Test |
| Rebecca | Sandbox-Test |
| Gary | Sandboxtest |
| Dorrie | Sandboxtest |

**Status**: ✅ Working


---

## Phase 3: Understanding the Code

### Backend Structure

```
backend/app/
├── main.py                 → API endpoints (routes)
├── healthlake_client.py    → Multi-source FHIR client (HealthLake, Epic, athenahealth)
├── bedrock_service.py      → Calls Claude AI for summaries
├── models.py               → Data structures (what data looks like)
└── config.py               → Configuration settings
```

**Key Concepts:**

**FastAPI (main.py)**:
- Web framework for Python
- Defines URLs like `/api/patients`
- Handles requests from frontend
- Accepts `fhir_source` parameter to switch between data sources

**FHIR Client (healthlake_client.py)**:
- Factory pattern supporting multiple FHIR sources
- AWS HealthLake with SigV4 authentication
- Epic with JWT (RS384) authentication
- athenahealth with JWT (RS384) authentication
- Parses FHIR format into simple Python objects

**Bedrock Service**:
- Sends patient data to Claude Sonnet 4
- Gets back human-readable summaries
- Handles follow-up questions with conversation history

---

### Frontend Structure

```
frontend/src/
├── App.tsx                      → Main application component
├── components/
│   ├── PatientList.tsx          → Left sidebar with patients
│   ├── PatientSummary.tsx       → Main view with patient details
│   └── ChatInterface.tsx        → Chat box for questions
├── services/
│   └── api.ts                   → API calls to backend
└── types.ts                     → TypeScript type definitions
```

**Key Concepts:**

**React Components**:
- Reusable pieces of UI
- Like LEGO blocks that build the website
- Each component handles one part of the interface

**API Service**:
- Functions that talk to backend
- Example: `getPatients()` fetches patient list
- Handles errors and loading states

**TypeScript**:
- JavaScript with types
- Catches errors before you run code
- Makes development easier

---

## Phase 5: Deploying to AWS

### 5.1 Set Up Pulumi (5 minutes)

**From project root:**
```bash
# Run the setup script
./scripts/setup-pulumi.sh
```

**You'll be asked to choose:**
1. **Pulumi Cloud** (recommended) - Free for individuals, automatic backups
2. **Local storage** - State files stored on your computer
3. **AWS S3** - State files in your own S3 bucket

**For beginners, choose option 1** (Pulumi Cloud):
```bash
# Create free account at: https://app.pulumi.com/signup
# Then login:
pulumi login
```

**Success looks like:**
```
✅ Pulumi setup complete!
```

**What this does**: 
- Creates Python virtual environment for Pulumi
- Installs Pulumi AWS dependencies
- Configures state storage (where Pulumi remembers what it created)

**Big Advantage**: Pulumi uses REAL PYTHON code, not YAML! Your IDE can help you with autocomplete and catch errors before you deploy.

---

### 5.2 Create Minimal Infrastructure (10 minutes)

**Run the dev script:**
```bash
# This creates just the basics (cheap!)
./scripts/start-dev.sh
```

**What gets created:**
- VPC (your private network)
- Subnets (network subdivisions)
- Security Groups (firewalls)
- IAM Roles (permissions)
- ECR Repositories (Docker image storage)

**Cost**: ~$0-5/month

---

### 5.3 Deploy Full Stack (20 minutes)

**When you're ready to test the full deployment:**
```bash
# This creates everything including load balancer
./scripts/start-testing.sh
```

**This will:**
1. Create full infrastructure (5 min)
2. Build Docker images (5 min)
3. Push to AWS ECR (2 min)
4. Deploy to ECS (5 min)
5. Show you the URL to access

**Cost**: ~$50-70/month while running

**Access your app:**
- Script will show URL like: `http://chart-agent-alb-123456.us-east-1.elb.amazonaws.com`
- Open that URL in browser
- Your app is now on the internet!

---

### 5.4 Tear Down (Save Money!)

**When done testing:**
```bash
# Scale back to minimal
./scripts/start-dev.sh

# Or destroy everything:
./scripts/teardown.sh
```

This deletes all AWS resources and stops charges.

---

## Troubleshooting

### "Command not found" errors

**Problem**: Terminal doesn't recognize `python3`, `node`, `pulumi`, etc.

**Solution**:
1. Make sure you installed the software
2. Restart your terminal
3. Check PATH: `echo $PATH`
4. Try reinstalling

---

### Backend won't start

**Problem**: Errors when running `uvicorn`

**Common fixes**:

1. **ModuleNotFoundError**:
   ```bash
   # Make sure virtual environment is activated
   source venv/bin/activate  # Mac/Linux
   venv\Scripts\activate     # Windows
   
   # Reinstall dependencies
   pip install -r requirements.txt
   ```

2. **AWS Credentials Error**:
   ```bash
   # Reconfigure AWS
   aws configure
   # Enter your keys again
   ```

3. **HealthLake Connection Error**:
   - Check your `.env` file has correct endpoint URL
   - Verify HealthLake data store is "Active" in AWS Console

---

### Frontend won't start

**Problem**: Errors when running `npm start`

**Common fixes**:

1. **Port 3000 in use**:
   ```bash
   # Kill other processes using port 3000
   # Mac/Linux:
   lsof -ti:3000 | xargs kill -9
   # Windows: Use Task Manager
   ```

2. **Module not found**:
   ```bash
   # Delete and reinstall
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **Can't connect to backend**:
   - Make sure backend terminal is still running
   - Check backend is on http://localhost:8000
   - Try http://localhost:8000/docs in browser

---

### AWS Permissions Errors

**Problem**: "AccessDenied" when accessing AWS services

**Solutions**:

1. **Check IAM permissions**:
   - Go to AWS Console → IAM
   - Find your user
   - Attach policy: `AdministratorAccess` (for dev/learning only!)

2. **Verify AWS credentials**:
   ```bash
   aws sts get-caller-identity
   # Should show your account info
   ```

3. **Check region**:
   - Make sure you're in `us-east-1`
   - Some services might not be available in all regions

---

### Docker Issues

**Problem**: Docker commands fail

**Solutions**:

1. **Make sure Docker Desktop is running**:
   - Open Docker Desktop app
   - Wait for green "Docker Desktop is running"

2. **Restart Docker**:
   - Quit Docker Desktop
   - Start it again
   - Wait 30 seconds

3. **Clean up Docker**:
   ```bash
   # Remove all containers and images
   docker system prune -a
   # Restart Docker Desktop
   ```

---

## Next Steps

### Learn More

**Beginner Resources**:
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [React Tutorial](https://react.dev/learn)
- [AWS Getting Started](https://aws.amazon.com/getting-started/)
- [Pulumi Documentation](https://www.pulumi.com/docs/)
- [Pulumi Python Guide](https://www.pulumi.com/docs/languages-sdks/python/)

**Project Documentation**:
- [README.md](README.md) - Project overview
- [GETTING_STARTED.md](GETTING_STARTED.md) - Quick start
- [docs/AWS_SETUP.md](docs/AWS_SETUP.md) - Detailed AWS guide
- [docs/EPIC_INTEGRATION.md](docs/EPIC_INTEGRATION.md) - Epic FHIR guide

### Customize the App

**Easy changes**:
1. **Change AI prompts**:
   - Edit `backend/app/bedrock_service.py`
   - Modify `_build_summary_prompt()` function

2. **Change UI colors**:
   - Edit `frontend/src/App.tsx`
   - Modify the `theme` object

3. **Add new features**:
   - Add endpoint in `backend/app/main.py`
   - Add component in `frontend/src/components/`

### Practice Exercises

1. **Add a new FHIR resource**:
   - Try fetching "Immunization" records
   - Add to HealthLake client
   - Display in frontend

2. **Customize the summary**:
   - Change what information Claude includes
   - Modify the prompt template

3. **Add error handling**:
   - Show better error messages
   - Add retry logic for failed requests

---

## Glossary

**API**: Application Programming Interface - how software talks to other software  
**AWS**: Amazon Web Services - cloud computing platform  
**Backend**: Server-side code that processes data  
**Bedrock**: AWS service for accessing AI models  
**Claude**: AI model that understands and generates text  
**Container**: Packaged application that runs consistently everywhere  
**Docker**: Tool for creating containers  
**ECS**: Elastic Container Service - runs Docker containers on AWS  
**Endpoint**: URL where API can be accessed  
**FHIR**: Fast Healthcare Interoperability Resources - standard for healthcare data  
**Frontend**: Client-side code (website users see)  
**HealthLake**: AWS service for storing healthcare data  
**IAM**: Identity and Access Management - AWS permissions system  
**Pulumi**: Modern Infrastructure as Code using real programming languages  
**React**: JavaScript library for building user interfaces  
**REST API**: Standard way for frontend and backend to communicate  
**S3**: Simple Storage Service - AWS file storage  
**VPC**: Virtual Private Cloud - isolated network in AWS  

---

## Getting Help

**When stuck**:
1. Read error messages carefully
2. Google the error message
3. Check AWS service health: https://status.aws.amazon.com/
4. Review this guide's Troubleshooting section
5. Check project documentation

**Remember**: Every developer gets stuck! Problem-solving is part of learning.

---

**You've completed the beginner's guide!** You now have:
- ✅ Development environment set up
- ✅ Application running locally with Docker
- ✅ Access to 3 FHIR data sources (HealthLake, Epic, athenahealth)
- ✅ AI-powered patient summaries with Claude Sonnet 4
- ✅ Understanding of project structure
- ✅ Ability to deploy to AWS
- ✅ Troubleshooting skills

---

## Current Project Status

| Feature | Status |
|---------|--------|
| AWS HealthLake | ✅ Working (48 patients) |
| Epic Sandbox | ✅ Working (7 patients) |
| athenahealth Sandbox | ✅ Working (7 patients) |
| Claude Sonnet 4 Summaries | ✅ Working |
| Follow-up Chat | ✅ Working |
| Docker Development | ✅ Working |
| JWT Authentication | ✅ Working (Epic & athenahealth) |

**Last Updated**: December 2024

**Happy coding!** 🚀

