"""Pydantic models for API requests and responses."""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class PractitionerBasic(BaseModel):
    """Basic practitioner information."""
    id: str
    name: str
    prefix: Optional[str] = None  # e.g., "Dr."
    specialty: Optional[str] = None


class PractitionerListResponse(BaseModel):
    """Response model for practitioner list."""
    practitioners: List[PractitionerBasic]
    total: int


class PatientBasic(BaseModel):
    """Basic patient information for list view."""
    id: str
    name: str
    mrn: Optional[str] = None
    dob: Optional[str] = None
    gender: Optional[str] = None
    appointment_time: Optional[str] = None
    general_practitioner_id: Optional[str] = None  # Reference to practitioner


class PatientListResponse(BaseModel):
    """Response model for patient list."""
    patients: List[PatientBasic]
    total: int


class Condition(BaseModel):
    """Patient condition/diagnosis."""
    code: str
    display: str
    clinical_status: Optional[str] = None
    onset_date: Optional[str] = None


class Medication(BaseModel):
    """Patient medication."""
    code: str
    display: str
    status: Optional[str] = None
    dosage: Optional[str] = None


class Observation(BaseModel):
    """Lab result or vital sign."""
    code: str
    display: str
    value: Optional[str] = None
    unit: Optional[str] = None
    date: Optional[str] = None
    abnormal: Optional[bool] = False


class Allergy(BaseModel):
    """Patient allergy."""
    code: str
    display: str
    criticality: Optional[str] = None
    reaction: Optional[str] = None


class Encounter(BaseModel):
    """Patient encounter/visit."""
    id: str
    type: Optional[str] = None
    date: Optional[str] = None
    reason: Optional[str] = None
    provider: Optional[str] = None


class PatientData(BaseModel):
    """Complete patient data from FHIR."""
    patient: PatientBasic
    conditions: List[Condition] = []
    medications: List[Medication] = []
    observations: List[Observation] = []
    allergies: List[Allergy] = []
    encounters: List[Encounter] = []


class SummaryRequest(BaseModel):
    """Request to generate patient summary."""
    patient_id: str


class SummaryResponse(BaseModel):
    """Response with AI-generated summary."""
    patient_id: str
    summary: str
    generated_at: datetime


class ChatMessage(BaseModel):
    """Chat message."""
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    """Request for chat/follow-up question."""
    patient_id: str
    question: str
    conversation_history: List[ChatMessage] = []


class ChatResponse(BaseModel):
    """Response from chat."""
    patient_id: str
    answer: str
    conversation_history: List[ChatMessage]


class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str
    environment: str
    healthlake_configured: bool
    bedrock_configured: bool

