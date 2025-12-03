"""FastAPI main application."""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import List, Optional

from app.config import settings
from app.models import (
    PatientListResponse, PatientData, SummaryRequest, SummaryResponse,
    ChatRequest, ChatResponse, ChatMessage, HealthCheckResponse,
    PractitionerListResponse
)
from app.healthlake_client import get_fhir_client, FHIR_SOURCES
from app.bedrock_service import BedrockService

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
            {"id": "healthlake", "name": "AWS HealthLake", "description": "Your HealthLake data store"},
            {"id": "epic", "name": "Epic Sandbox", "description": "Epic's open FHIR sandbox"},
            {"id": "athena", "name": "athenahealth Sandbox", "description": "athenahealth Preview API"},
            {"id": "demo", "name": "Public FHIR Server", "description": "HAPI FHIR public test server"}
        ],
        "default": "healthlake"
    }


@app.get("/api/practitioners", response_model=PractitionerListResponse)
async def get_practitioners(
    count: int = 50,
    fhir_source: Optional[str] = Query(None, description="FHIR source: healthlake, epic, or demo")
):
    """Get list of practitioners."""
    try:
        client = get_fhir_client(fhir_source)
        practitioners = client.search_practitioners(count=count)
        return PractitionerListResponse(
            practitioners=practitioners,
            total=len(practitioners)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching practitioners: {str(e)}")


@app.get("/api/patients", response_model=PatientListResponse)
async def get_patients(
    count: int = 50, 
    practitioner_id: Optional[str] = None,
    fhir_source: Optional[str] = Query(None, description="FHIR source: healthlake, epic, or demo")
):
    """Get list of patients, optionally filtered by practitioner."""
    try:
        client = get_fhir_client(fhir_source)
        patients = client.search_patients(count=count, practitioner_id=practitioner_id)
        return PatientListResponse(
            patients=patients,
            total=len(patients)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching patients: {str(e)}")


@app.get("/api/patients/{patient_id}", response_model=PatientData)
async def get_patient_data(
    patient_id: str,
    fhir_source: Optional[str] = Query(None, description="FHIR source: healthlake, epic, or demo")
):
    """Get complete data for a specific patient."""
    try:
        client = get_fhir_client(fhir_source)
        patient_data = client.get_patient_data(patient_id)
        return patient_data
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching patient data: {str(e)}")


@app.post("/api/patients/{patient_id}/summary", response_model=SummaryResponse)
async def generate_summary(
    patient_id: str,
    fhir_source: Optional[str] = Query(None, description="FHIR source: healthlake, epic, or demo")
):
    """Generate AI summary for patient."""
    try:
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
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")


@app.post("/api/patients/{patient_id}/chat", response_model=ChatResponse)
async def chat(
    patient_id: str, 
    request: ChatRequest,
    fhir_source: Optional[str] = Query(None, description="FHIR source: healthlake, epic, or demo")
):
    """Answer follow-up question about patient."""
    try:
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

