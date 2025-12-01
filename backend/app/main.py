"""FastAPI main application."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import List

from app.config import settings
from app.models import (
    PatientListResponse, PatientData, SummaryRequest, SummaryResponse,
    ChatRequest, ChatResponse, ChatMessage, HealthCheckResponse
)
from app.healthlake_client import HealthLakeClient
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

# Initialize clients
healthlake_client = HealthLakeClient()
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


@app.get("/api/patients", response_model=PatientListResponse)
async def get_patients(count: int = 50):
    """Get list of patients."""
    try:
        patients = healthlake_client.search_patients(count=count)
        return PatientListResponse(
            patients=patients,
            total=len(patients)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching patients: {str(e)}")


@app.get("/api/patients/{patient_id}", response_model=PatientData)
async def get_patient_data(patient_id: str):
    """Get complete data for a specific patient."""
    try:
        patient_data = healthlake_client.get_patient_data(patient_id)
        return patient_data
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching patient data: {str(e)}")


@app.post("/api/patients/{patient_id}/summary", response_model=SummaryResponse)
async def generate_summary(patient_id: str):
    """Generate AI summary for patient."""
    try:
        # Get patient data
        patient_data = healthlake_client.get_patient_data(patient_id)
        
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
async def chat(patient_id: str, request: ChatRequest):
    """Answer follow-up question about patient."""
    try:
        # Get patient data
        patient_data = healthlake_client.get_patient_data(patient_id)
        
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

