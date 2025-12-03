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
        ]) if patient_data.conditions else "- None documented"
        
        # Format medications
        medications_text = "\n".join([
            f"- {m.display} {m.dosage if m.dosage else ''}"
            for m in patient_data.medications
        ]) if patient_data.medications else "- None documented"
        
        # Format recent labs with abnormal flags
        observations_text = "\n".join([
            f"- {o.display}: {o.value} {o.unit} ({o.date[:10] if o.date else 'Unknown'})" + 
            (" [ABNORMAL]" if o.abnormal else " [NORMAL]")
            for o in patient_data.observations[:10]
        ]) if patient_data.observations else "- No recent labs"
        
        # Format allergies with severity
        allergies_text = "\n".join([
            f"- ⚠️ {a.display} ({a.criticality.upper() if a.criticality else 'UNKNOWN'} criticality) - {a.reaction or 'Reaction not specified'}"
            for a in patient_data.allergies
        ]) if patient_data.allergies else "- No known allergies (NKDA)"
        
        # Format recent encounters
        encounters_text = "\n".join([
            f"- {e.date[:10] if e.date else 'Unknown date'}: {e.type} - {e.reason or 'Reason not documented'}"
            for e in patient_data.encounters[:5]
        ]) if patient_data.encounters else "- No recent visits documented"
        
        prompt = f"""You are a clinical AI assistant preparing a pre-appointment summary for a healthcare provider. Generate a concise, clinically actionable overview optimized for rapid review.

## PATIENT DEMOGRAPHICS
- **Name:** {patient.name} | **MRN:** {patient.mrn or 'N/A'}
- **Age:** {self._calculate_age(patient.dob) if patient.dob else 'Unknown'} | **Gender:** {patient.gender or 'Unknown'}

## CLINICAL DATA

**Active Conditions:**
{conditions_text}

**Recent Encounters (Last 6 months):**
{encounters_text}

**Current Medications:**
{medications_text}

**Recent Laboratory Results:**
{observations_text}

**Allergies & Adverse Reactions:**
{allergies_text}

---

## REQUIRED OUTPUT

Provide a structured clinical summary using the following format:

**1. Clinical Priority Items**
- List active conditions requiring monitoring or intervention
- Flag any concerning trends or uncontrolled conditions

**2. Visit Context**
- Summarize recent encounters and their outcomes
- Note any pattern of utilization (e.g., frequent ED visits)

**3. Laboratory Review**
- Highlight abnormal values with clinical significance
- Note trends if prior results available

**4. Medication Safety Check**
- Confirm appropriate dosing given renal function
- Identify high-risk medications (anticoagulants, diabetes meds, etc.)
- Flag potential drug-disease interactions

**5. Critical Safety Alerts**
- Document severe allergies and contraindications
- Note any drug-drug interactions in current regimen

**Formatting Requirements:**
- Use bullet points for scannability
- Bold key clinical terms and abnormal findings
- Limit to 150-200 words total
- Prioritize actionable information over background details"""
        
        return prompt
    
    def _build_chat_system_prompt(self, patient_data: PatientData) -> str:
        """Build system prompt for chat with patient context."""
        patient = patient_data.patient
        
        # Format patient data for context
        conditions = ", ".join([c.display for c in patient_data.conditions[:10]]) or "None documented"
        medications = ", ".join([m.display for m in patient_data.medications[:10]]) or "None documented"
        allergies = ", ".join([f"{a.display} ({a.criticality})" for a in patient_data.allergies]) or "NKDA"
        
        system_prompt = f"""You are a clinical decision support AI assistant helping a healthcare provider review the medical record for patient {patient.name} (MRN: {patient.mrn or 'N/A'}).

## PATIENT CONTEXT

- **Age:** {self._calculate_age(patient.dob) if patient.dob else 'Unknown'} | **Gender:** {patient.gender or 'Unknown'}
- **Active Conditions:** {conditions}
- **Current Medications:** {medications}
- **Allergies:** {allergies} [CRITICAL - verify before prescribing]

## YOUR ROLE & CAPABILITIES

You have access to this patient's complete medical record including:
- Problem list and diagnoses
- Medication history (active and historical)
- Laboratory and imaging results
- Clinical encounters and notes
- Procedures and immunizations

## RESPONSE REQUIREMENTS

**Always:**
- Provide accurate, evidence-based clinical information
- **Cite specific sources:** Include dates, values, and document types (e.g., "HbA1c 7.2% on 2024-01-10" or "Per 2024-02-15 progress note")
- Use precise medical terminology appropriate for a licensed provider
- Distinguish between clinical facts and clinical interpretation
- Prioritize patient safety considerations

**Never:**
- Make diagnostic conclusions - present data for provider interpretation
- Recommend specific treatments without caveats about clinical judgment
- Ignore or downplay allergy information
- Provide information not present in the medical record

**If information is unavailable:**
- State clearly: "This information is not documented in the available record"
- Suggest where the provider might find it (e.g., "Consider ordering [test]" or "May need to obtain records from [source]")
- Do NOT speculate or fill gaps with general medical knowledge

**Response style:**
- **Concise:** Answer the specific question asked; avoid unnecessary background
- **Structured:** Use bullet points or short paragraphs for readability
- **Contextual:** When relevant, note if findings are abnormal, trending, or require follow-up
- **Time-aware:** Prioritize recent data but note historical context when clinically relevant"""
        
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

