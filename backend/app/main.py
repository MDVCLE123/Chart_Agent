"""FastAPI main application."""
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from typing import List, Optional

from app.config import settings
from app.models import (
    PatientListResponse, PatientData, SummaryRequest, SummaryResponse,
    ChatRequest, ChatResponse, ChatMessage, HealthCheckResponse,
    PractitionerListResponse
)
from app.healthlake_client import get_fhir_client, FHIR_SOURCES
from app.bedrock_service import BedrockService

# Choose auth module based on configuration
if settings.use_cognito and settings.cognito_user_pool_id:
    print("🔐 Using AWS Cognito for authentication")
    from app.cognito_auth import (
        authenticate_user, get_current_user, require_admin,
        Token, LoginRequest, User,
        UserCreate, UserUpdate, UserResponse,
        get_all_users, create_user, update_user, delete_user,
    )
    USE_COGNITO = True
else:
    print("🔐 Using local authentication")
    from app.auth import (
        authenticate_user, create_access_token, get_current_user, require_admin,
        Token, LoginRequest, User, ACCESS_TOKEN_EXPIRE_MINUTES,
        UserCreate, UserUpdate, UserResponse,
        get_all_users, create_user, update_user, delete_user,
        AVAILABLE_DATA_SOURCES
    )
    USE_COGNITO = False

# Initialize FastAPI app
app = FastAPI(
    title="Chart Preparation Agent API",
    description="AI-powered chart preparation for healthcare providers",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Bedrock service (stateless, can be shared)
bedrock_service = BedrockService()


@app.get("/api/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint."""
    return HealthCheckResponse(
        status="healthy",
        environment=settings.environment,
        healthlake_configured=bool(settings.healthlake_datastore_endpoint),
        bedrock_configured=bool(settings.bedrock_model_id)
    )


@app.get("/api/fhir-sources")
async def get_fhir_sources():
    """Get available FHIR data sources."""
    return {
        "sources": [
            {"id": "healthlake", "name": "AWS HealthLake", "icon": "☁️", "description": "Your HealthLake data store"},
            {"id": "epic", "name": "Epic Sandbox", "icon": "🏥", "description": "Epic's FHIR sandbox (7 patients)"},
            {"id": "athena", "name": "athenahealth Sandbox", "icon": "💚", "description": "athenahealth Preview API"}
        ],
        "default": "healthlake"
    }


@app.get("/api/practitioners", response_model=PractitionerListResponse)
async def get_practitioners(
    count: int = 50,
    fhir_source: Optional[str] = Query(None, description="FHIR source: healthlake, epic, or demo"),
    current_user: User = Depends(get_current_user)
):
    """Get list of practitioners."""
    try:
        # Validate user has access to requested data source
        source = fhir_source or "healthlake"
        if source not in current_user.allowed_data_sources:
            raise HTTPException(status_code=403, detail=f"Access denied to data source: {source}")
        
        client = get_fhir_client(fhir_source)
        practitioners = client.search_practitioners(count=count)
        return PractitionerListResponse(
            practitioners=practitioners,
            total=len(practitioners)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching practitioners: {str(e)}")


@app.get("/api/patients", response_model=PatientListResponse)
async def get_patients(
    count: int = 50, 
    practitioner_id: Optional[str] = None,
    fhir_source: Optional[str] = Query(None, description="FHIR source: healthlake, epic, or demo"),
    current_user: User = Depends(get_current_user)
):
    """Get list of patients, optionally filtered by practitioner."""
    try:
        # Validate user has access to requested data source
        source = fhir_source or "healthlake"
        if source not in current_user.allowed_data_sources:
            raise HTTPException(status_code=403, detail=f"Access denied to data source: {source}")
        
        client = get_fhir_client(fhir_source)
        patients = client.search_patients(count=count, practitioner_id=practitioner_id)
        return PatientListResponse(
            patients=patients,
            total=len(patients)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching patients: {str(e)}")


@app.get("/api/patients/{patient_id}", response_model=PatientData)
async def get_patient_data(
    patient_id: str,
    fhir_source: Optional[str] = Query(None, description="FHIR source: healthlake, epic, or demo"),
    current_user: User = Depends(get_current_user)
):
    """Get complete data for a specific patient."""
    try:
        # Validate user has access to requested data source
        source = fhir_source or "healthlake"
        if source not in current_user.allowed_data_sources:
            raise HTTPException(status_code=403, detail=f"Access denied to data source: {source}")
        
        client = get_fhir_client(fhir_source)
        patient_data = client.get_patient_data(patient_id)
        return patient_data
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching patient data: {str(e)}")


@app.post("/api/patients/{patient_id}/summary", response_model=SummaryResponse)
async def generate_summary(
    patient_id: str,
    fhir_source: Optional[str] = Query(None, description="FHIR source: healthlake, epic, or demo"),
    current_user: User = Depends(get_current_user)
):
    """Generate AI summary for patient."""
    try:
        # Validate user has access to requested data source
        source = fhir_source or "healthlake"
        if source not in current_user.allowed_data_sources:
            raise HTTPException(status_code=403, detail=f"Access denied to data source: {source}")
        
        # Get patient data from specified source
        client = get_fhir_client(fhir_source)
        patient_data = client.get_patient_data(patient_id)
        
        # Generate summary using Bedrock
        summary = bedrock_service.generate_summary(patient_data)
        
        return SummaryResponse(
            patient_id=patient_id,
            summary=summary,
            generated_at=datetime.now()
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")


@app.post("/api/patients/{patient_id}/chat", response_model=ChatResponse)
async def chat(
    patient_id: str, 
    request: ChatRequest,
    fhir_source: Optional[str] = Query(None, description="FHIR source: healthlake, epic, or demo"),
    current_user: User = Depends(get_current_user)
):
    """Answer follow-up question about patient."""
    try:
        # Validate user has access to requested data source
        source = fhir_source or "healthlake"
        if source not in current_user.allowed_data_sources:
            raise HTTPException(status_code=403, detail=f"Access denied to data source: {source}")
        
        # Get patient data from specified source
        client = get_fhir_client(fhir_source)
        patient_data = client.get_patient_data(patient_id)
        
        # Get answer from Bedrock
        answer = bedrock_service.answer_question(
            question=request.question,
            patient_data=patient_data,
            conversation_history=request.conversation_history
        )
        
        # Update conversation history
        updated_history = request.conversation_history + [
            ChatMessage(role="user", content=request.question),
            ChatMessage(role="assistant", content=answer)
        ]
        
        return ChatResponse(
            patient_id=patient_id,
            answer=answer,
            conversation_history=updated_history
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in chat: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Chart Preparation Agent API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


# ============== Authentication Endpoints ==============

@app.post("/api/auth/login")
async def login(request: LoginRequest):
    """Authenticate user and return token."""
    result = authenticate_user(request.username, request.password)
    if not result:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if USE_COGNITO:
        # Cognito returns all token info directly
        return {
            "access_token": result['access_token'],
            "id_token": result.get('id_token', ''),
            "refresh_token": result.get('refresh_token', ''),
            "token_type": "bearer",
            "expires_in": result.get('expires_in', 3600),
            "user": result['user']
        }
    else:
        # Local auth - create JWT token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": result.username, "role": result.role},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "username": result.email or result.username,
                "email": result.email or result.username,
                "first_name": result.first_name,
                "last_name": result.last_name,
                "role": result.role,
                "allowed_data_sources": result.allowed_data_sources,
                "practitioner_id": result.practitioner_id,
                "practitioner_name": result.practitioner_name
            }
        }


@app.get("/api/auth/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user info."""
    # Handle both Cognito (has first_name/last_name) and local auth (may not)
    if hasattr(current_user, 'first_name'):
        # Cognito or updated local auth
        return {
            "username": current_user.email or current_user.username,
            "email": current_user.email or current_user.username,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "role": current_user.role,
            "allowed_data_sources": current_user.allowed_data_sources,
            "practitioner_id": current_user.practitioner_id,
            "practitioner_name": current_user.practitioner_name
        }
    else:
        # Legacy local auth with full_name - convert to first/last
        full_name = getattr(current_user, 'full_name', None) or ''
        name_parts = full_name.split(' ', 1) if full_name else []
        return {
            "username": current_user.email or current_user.username,
            "email": current_user.email or current_user.username,
            "first_name": name_parts[0] if len(name_parts) > 0 else None,
            "last_name": name_parts[1] if len(name_parts) > 1 else None,
            "role": current_user.role,
            "allowed_data_sources": current_user.allowed_data_sources,
            "practitioner_id": current_user.practitioner_id,
            "practitioner_name": current_user.practitioner_name
        }


@app.post("/api/auth/verify")
async def verify_token(current_user: User = Depends(get_current_user)):
    """Verify if token is valid."""
    return {"valid": True, "username": current_user.username}


# ============== User Management Endpoints (Admin Only) ==============

@app.get("/api/admin/users", response_model=List[UserResponse])
async def list_users(current_user: User = Depends(require_admin)):
    """Get list of all users (admin only)."""
    return get_all_users()


@app.post("/api/admin/users", response_model=UserResponse)
async def create_new_user(user_data: UserCreate, current_user: User = Depends(require_admin)):
    """Create a new user (admin only)."""
    try:
        return create_user(user_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/api/admin/users/{username}", response_model=UserResponse)
async def update_existing_user(
    username: str, 
    user_data: UserUpdate, 
    current_user: User = Depends(require_admin)
):
    """Update an existing user (admin only)."""
    try:
        return update_user(username, user_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/admin/users/{username}")
async def delete_existing_user(username: str, current_user: User = Depends(require_admin)):
    """Delete a user (admin only)."""
    try:
        delete_user(username)
        return {"message": f"User '{username}' deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/admin/data-sources")
async def get_available_data_sources(current_user: User = Depends(require_admin)):
    """Get list of available data sources for user permissions."""
    return {
        "sources": [
            {"id": "healthlake", "name": "AWS HealthLake", "icon": "☁️"},
            {"id": "epic", "name": "Epic Sandbox", "icon": "🏥"},
            {"id": "athena", "name": "athenahealth", "icon": "💚"}
        ]
    }


@app.get("/.well-known/jwks.json")
async def get_jwks():
    """Serve JWKS for Epic OAuth2 authentication."""
    return {
        "keys": [
            {
                "kty": "RSA",
                "alg": "RS384",
                "use": "sig",
                "kid": "chart-agent-key-1",
                "n": "y8XrkBdGJO_ICywKZ7E1rUk88u_HIAAKQCZPt8yY9FrphayLRl8x3zFwggm3Z_pa0haXh70Vb2Ogt9YcsGU7E-NTjRG833JLdxmfuPWDmlOckpr41L5jvrc9FugFP807OzUW7BVvF7sqLPNJdaJyuRGjGXYwaz1NALWDwaKhVni6KjPJaZQZ-TM43gYeCuvjoxZk18Ztp-92opiWRiLiuhJZjxw2OmqXkW4r_REBI1VVzVzHIG7HeNhVqEJ_imNQRrGFwDDr0Nd3nkLVI-2qOso2rDrWpG3_dMVxY6jT_AM1vEeQMMxS3E4BMYVig03CQBJXWtm4tdvFSqj0wv8qLQ",
                "e": "AQAB"
            }
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

