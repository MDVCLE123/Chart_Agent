"""AWS Bedrock service for Claude AI integration."""
import boto3
import json
from typing import List, Dict, Any
from datetime import datetime

from app.config import settings
from app.models import PatientData, ChatMessage


class BedrockService:
    """Service for interacting with AWS Bedrock (Claude)."""
    
    def __init__(self):
        self.client = boto3.client(
            'bedrock-runtime',
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id if settings.aws_access_key_id else None,
            aws_secret_access_key=settings.aws_secret_access_key if settings.aws_secret_access_key else None
        )
        self.model_id = settings.bedrock_model_id
    
    def generate_summary(self, patient_data: PatientData) -> str:
        """Generate clinical summary for patient using Claude."""
        prompt = self._build_summary_prompt(patient_data)
        
        try:
            response = self._invoke_claude(prompt)
            return response
        except Exception as e:
            print(f"Error generating summary: {e}")
            return f"Error generating summary: {str(e)}"
    
    def answer_question(
        self, 
        question: str, 
        patient_data: PatientData,
        conversation_history: List[ChatMessage] = None
    ) -> str:
        """Answer follow-up question about patient using Claude."""
        if conversation_history is None:
            conversation_history = []
        
        # Build conversation with patient context
        system_prompt = self._build_chat_system_prompt(patient_data)
        
        # Convert history to Claude format
        messages = []
        for msg in conversation_history:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Add current question
        messages.append({
            "role": "user",
            "content": question
        })
        
        try:
            response = self._invoke_claude_with_history(system_prompt, messages)
            return response
        except Exception as e:
            print(f"Error answering question: {e}")
            return f"Error: {str(e)}"
    
    def _invoke_claude(self, prompt: str, max_tokens: int = 4000) -> str:
        """Invoke Claude model via Bedrock."""
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7
        })
        
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=body
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']
    
    def _invoke_claude_with_history(
        self, 
        system_prompt: str, 
        messages: List[Dict[str, str]]
    ) -> str:
        """Invoke Claude with conversation history."""
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2000,
            "system": system_prompt,
            "messages": messages,
            "temperature": 0.7
        })
        
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=body
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']
    
    def _build_summary_prompt(self, patient_data: PatientData) -> str:
        """Build prompt for clinical summary generation."""
        patient = patient_data.patient
        
        # Format conditions
        conditions_text = "\n".join([
            f"- {c.display} (Status: {c.clinical_status}, Onset: {c.onset_date})"
            for c in patient_data.conditions
        ]) if patient_data.conditions else "None documented"
        
        # Format medications
        medications_text = "\n".join([
            f"- {m.display} ({m.dosage if m.dosage else 'Dosage not specified'})"
            for m in patient_data.medications
        ]) if patient_data.medications else "None documented"
        
        # Format recent labs
        observations_text = "\n".join([
            f"- {o.display}: {o.value} {o.unit} on {o.date[:10] if o.date else 'Unknown'}" + 
            (" [ABNORMAL]" if o.abnormal else "")
            for o in patient_data.observations[:10]
        ]) if patient_data.observations else "No recent labs"
        
        # Format allergies
        allergies_text = "\n".join([
            f"- {a.display} (Criticality: {a.criticality}, Reaction: {a.reaction})"
            for a in patient_data.allergies
        ]) if patient_data.allergies else "No known allergies"
        
        # Format recent encounters
        encounters_text = "\n".join([
            f"- {e.date[:10] if e.date else 'Unknown date'}: {e.type} - {e.reason}"
            for e in patient_data.encounters[:5]
        ]) if patient_data.encounters else "No recent visits documented"
        
        prompt = f"""You are a clinical AI assistant helping a healthcare provider prepare for a patient appointment. Provide a concise, clinically relevant summary.

PATIENT INFORMATION:
Name: {patient.name}
Age: {self._calculate_age(patient.dob) if patient.dob else 'Unknown'}
Gender: {patient.gender or 'Unknown'}
MRN: {patient.mrn or 'N/A'}

ACTIVE CONDITIONS:
{conditions_text}

RECENT VISITS (Last 6 months):
{encounters_text}

CURRENT MEDICATIONS:
{medications_text}

RECENT LABS:
{observations_text}

ALLERGIES:
{allergies_text}

TASK: Provide a concise clinical summary highlighting:
1. Key active conditions requiring attention
2. Recent visit context and outcomes
3. Relevant lab findings (flag abnormal values)
4. Current medication regimen (note any high-risk meds)
5. Important safety considerations (allergies, drug interactions)

Format as bullet points for quick review before the appointment. Focus on actionable clinical information."""
        
        return prompt
    
    def _build_chat_system_prompt(self, patient_data: PatientData) -> str:
        """Build system prompt for chat with patient context."""
        patient = patient_data.patient
        
        # Abbreviated patient data for context
        conditions = ", ".join([c.display for c in patient_data.conditions[:5]])
        medications = ", ".join([m.display for m in patient_data.medications[:5]])
        
        system_prompt = f"""You are a clinical AI assistant. The provider is reviewing patient {patient.name}.

Patient Context:
- Age: {self._calculate_age(patient.dob) if patient.dob else 'Unknown'}
- Gender: {patient.gender or 'Unknown'}
- Key Conditions: {conditions if conditions else 'None documented'}
- Current Medications: {medications if medications else 'None documented'}

You have access to their complete medical record. Answer questions accurately and concisely.
Cite specific dates and values when relevant. If information is not in the record, say so clearly.
Focus on providing clinically relevant information to help the provider."""
        
        return system_prompt
    
    def _calculate_age(self, dob: str) -> str:
        """Calculate age from date of birth."""
        try:
            birth_date = datetime.strptime(dob, "%Y-%m-%d")
            today = datetime.now()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            return f"{age} years"
        except:
            return "Unknown"

