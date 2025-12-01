# Epic FHIR Sandbox Integration Guide

Complete guide for integrating with Epic's FHIR sandbox and production environments.

## Overview

Epic uses the SMART on FHIR standard for third-party app integration. This allows Chart Preparation Agent to access patient data securely using OAuth2 authentication.

## Prerequisites

- Epic FHIR sandbox account
- Registered application in Epic's App Orchard
- OAuth2 client credentials

## Step 1: Register Your Application

### Via Epic App Orchard

1. Go to [Epic FHIR](https://fhir.epic.com/)
2. Click "Build Apps"
3. Create a new application:
   - **App Name**: Chart Preparation Agent
   - **App Type**: Backend Service App (for server-to-server)
   - **Redirect URI**: Not needed for backend service apps
   - **Scopes**: Select required scopes:
     - `patient/*.read` - Read patient data
     - `launch` - Launch context
     - `online_access` - Maintain session

4. Note your **Client ID** and generate a **Client Secret**

## Step 2: Configure Backend for Epic

Update `backend/app/config.py` to add Epic configuration:

```python
class Settings(BaseSettings):
    # ... existing settings ...
    
    # Epic FHIR Configuration
    epic_fhir_base_url: str = ""
    epic_client_id: str = ""
    epic_client_secret: str = ""
    
    # Data source selection
    fhir_source: str = "healthlake"  # or "epic"
```

Update `.env`:

```bash
# Epic FHIR Configuration
EPIC_FHIR_BASE_URL=https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4
EPIC_CLIENT_ID=your_client_id_here
EPIC_CLIENT_SECRET=your_client_secret_here
FHIR_SOURCE=epic
```

## Step 3: Update FHIR Client Factory

Create an adapter pattern in `backend/app/fhir_adapter.py`:

```python
from app.config import settings
from app.healthlake_client import HealthLakeClient
from app.epic_client import EpicFHIRClient

class FHIRClientFactory:
    @staticmethod
    def get_client():
        """Get appropriate FHIR client based on configuration."""
        if settings.fhir_source == "epic":
            return EpicFHIRClient(
                base_url=settings.epic_fhir_base_url,
                client_id=settings.epic_client_id,
                client_secret=settings.epic_client_secret
            )
        else:
            return HealthLakeClient()
```

Update `backend/app/main.py`:

```python
from app.fhir_adapter import FHIRClientFactory

# Initialize client
fhir_client = FHIRClientFactory.get_client()
```

## Step 4: Test with Epic Sandbox

### Available Test Patients

Epic provides several test patients in their sandbox:

- **Derrick Lin** (Patient ID: `Tbt3KuCY0B5PSrJvCu2j-PlK.aiHsu2xUjUM8bWpetXoB`)
- **Desiree Powell** (Patient ID: `eM0XP9lNpghjMljxHU9lxuz0KgWauCVQDY8yLHUifIc03`)
- **Betty Jennings** (Patient ID: `erXuFYUfucBZaryVksYEcMg3`)

### Test API Calls

```bash
# Get patient data
curl -X GET \
  'https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/Patient/Tbt3KuCY0B5PSrJvCu2j-PlK.aiHsu2xUjUM8bWpetXoB' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
  -H 'Accept: application/fhir+json'
```

### Run Tests

```bash
# Start backend with Epic configuration
cd backend
export FHIR_SOURCE=epic
uvicorn app.main:app --reload

# Test endpoints
curl http://localhost:8000/api/patients
curl http://localhost:8000/api/patients/Tbt3KuCY0B5PSrJvCu2j-PlK.aiHsu2xUjUM8bWpetXoB
```

## Step 5: Handle OAuth2 Flow

For production deployments with provider authentication:

### Backend Changes

Add SMART on FHIR OAuth2 flow:

```python
from authlib.integrations.starlette_client import OAuth

oauth = OAuth()
oauth.register(
    name='epic',
    client_id=settings.epic_client_id,
    client_secret=settings.epic_client_secret,
    authorize_url='https://fhir.epic.com/interconnect-fhir-oauth/oauth2/authorize',
    access_token_url='https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token',
    api_base_url='https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4',
)

@app.get('/auth/epic/login')
async def epic_login(request: Request):
    redirect_uri = request.url_for('epic_callback')
    return await oauth.epic.authorize_redirect(request, redirect_uri)

@app.get('/auth/epic/callback')
async def epic_callback(request: Request):
    token = await oauth.epic.authorize_access_token(request)
    # Store token for user session
    return token
```

## Step 6: Production Deployment

### Epic Production Requirements

1. **App Review**: Submit app for Epic's app review process
2. **Security Audit**: Complete Epic's security questionnaire
3. **HIPAA Compliance**: Ensure BAA with Epic
4. **Testing**: Complete Epic's certification testing

### Production Configuration

Update environment for production:

```bash
EPIC_FHIR_BASE_URL=https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/prod
EPIC_CLIENT_ID=production_client_id
EPIC_CLIENT_SECRET=production_client_secret
FHIR_SOURCE=epic
```

## Multi-EHR Support

To support multiple EHRs simultaneously:

### Configuration

```python
# Support both HealthLake and Epic
FHIR_SOURCES = {
    "healthlake": {
        "enabled": True,
        "endpoint": os.getenv("HEALTHLAKE_DATASTORE_ENDPOINT")
    },
    "epic": {
        "enabled": True,
        "base_url": os.getenv("EPIC_FHIR_BASE_URL"),
        "client_id": os.getenv("EPIC_CLIENT_ID"),
        "client_secret": os.getenv("EPIC_CLIENT_SECRET")
    }
}
```

### Runtime Selection

```python
@app.get("/api/patients/{patient_id}")
async def get_patient_data(
    patient_id: str,
    source: str = Query("healthlake", description="FHIR source")
):
    client = FHIRClientFactory.get_client(source)
    return client.get_patient_data(patient_id)
```

## Troubleshooting

### Access Token Issues

**Problem**: `401 Unauthorized` errors

**Solutions**:
- Verify client ID and secret are correct
- Check token hasn't expired (refresh before expiry)
- Ensure scopes are correct

### Patient Not Found

**Problem**: `404 Not Found` for patient queries

**Solutions**:
- Verify patient ID format is correct
- Check patient exists in sandbox
- Ensure you're using the correct base URL

### Rate Limiting

**Problem**: `429 Too Many Requests`

**Solutions**:
- Implement exponential backoff
- Cache responses appropriately
- Reduce number of API calls

### FHIR Version Mismatch

**Problem**: Unexpected response structures

**Solutions**:
- Epic uses FHIR R4 - ensure compatibility
- Check Epic's FHIR implementation guide
- Use Epic's capability statement endpoint

## Testing Checklist

- [ ] OAuth2 authentication works
- [ ] Can retrieve patient list
- [ ] Can fetch individual patient data
- [ ] Conditions are parsed correctly
- [ ] Medications are retrieved
- [ ] Lab results/observations work
- [ ] Allergies are displayed
- [ ] Recent encounters load
- [ ] Claude summary generation works with Epic data
- [ ] Chat interface functions with Epic data
- [ ] Error handling works correctly
- [ ] Token refresh happens automatically

## Resources

- [Epic FHIR Documentation](https://fhir.epic.com/)
- [Epic App Orchard](https://appmarket.epic.com/)
- [SMART on FHIR Specification](http://www.hl7.org/fhir/smart-app-launch/)
- [Epic FHIR Implementation Guide](https://fhir.epic.com/Documentation)

## Next Steps

After Epic integration:

1. Test with Cerner sandbox
2. Add support for Meditech
3. Test with Allscripts
4. Create unified EHR adapter interface
5. Add EHR auto-detection

