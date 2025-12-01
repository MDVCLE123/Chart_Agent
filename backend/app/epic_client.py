"""Epic FHIR client for sandbox and production integration."""
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from app.models import (
    PatientBasic, Condition, Medication, Observation, 
    Allergy, Encounter, PatientData
)


class EpicFHIRClient:
    """Client for interacting with Epic FHIR API."""
    
    def __init__(self, base_url: str, client_id: str, client_secret: str):
        """
        Initialize Epic FHIR client.
        
        Args:
            base_url: Epic FHIR base URL (e.g., https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4)
            client_id: Epic OAuth2 client ID
            client_secret: Epic OAuth2 client secret
        """
        self.base_url = base_url.rstrip('/')
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_expiry = None
    
    def _get_access_token(self) -> str:
        """Get OAuth2 access token using client credentials flow."""
        # Check if we have a valid token
        if self.access_token and self.token_expiry and datetime.now() < self.token_expiry:
            return self.access_token
        
        # Get token endpoint from base URL
        token_url = f"{self.base_url.split('/api')[0]}/oauth2/token"
        
        response = requests.post(
            token_url,
            data={
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        response.raise_for_status()
        
        token_data = response.json()
        self.access_token = token_data['access_token']
        # Set expiry to be 5 minutes before actual expiry
        expires_in = token_data.get('expires_in', 3600)
        self.token_expiry = datetime.now() + timedelta(seconds=expires_in - 300)
        
        return self.access_token
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make authenticated request to Epic FHIR API."""
        token = self._get_access_token()
        url = f"{self.base_url}/{endpoint}"
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/fhir+json'
        }
        
        response = requests.get(url, headers=headers, params=params or {})
        response.raise_for_status()
        return response.json()
    
    def search_patients(self, count: int = 50) -> List[PatientBasic]:
        """Search for patients in Epic."""
        try:
            bundle = self._make_request('Patient', {'_count': count})
            
            patients = []
            if "entry" in bundle:
                for entry in bundle["entry"]:
                    resource = entry.get("resource", {})
                    patients.append(self._parse_patient_basic(resource))
            
            return patients
        except Exception as e:
            print(f"Error searching patients: {e}")
            return []
    
    def get_patient(self, patient_id: str) -> Optional[PatientBasic]:
        """Get a specific patient by ID."""
        try:
            resource = self._make_request(f'Patient/{patient_id}')
            return self._parse_patient_basic(resource)
        except Exception as e:
            print(f"Error getting patient {patient_id}: {e}")
            return None
    
    def get_patient_data(self, patient_id: str) -> PatientData:
        """Fetch all relevant data for a patient."""
        patient = self.get_patient(patient_id)
        if not patient:
            raise ValueError(f"Patient {patient_id} not found")
        
        # Fetch all resources
        conditions = self._get_conditions(patient_id)
        medications = self._get_medications(patient_id)
        observations = self._get_observations(patient_id)
        allergies = self._get_allergies(patient_id)
        encounters = self._get_encounters(patient_id)
        
        return PatientData(
            patient=patient,
            conditions=conditions,
            medications=medications,
            observations=observations,
            allergies=allergies,
            encounters=encounters
        )
    
    def _get_conditions(self, patient_id: str) -> List[Condition]:
        """Get patient conditions."""
        try:
            bundle = self._make_request(
                'Condition',
                {'patient': patient_id, 'clinical-status': 'active'}
            )
            
            conditions = []
            if "entry" in bundle:
                for entry in bundle["entry"]:
                    resource = entry.get("resource", {})
                    condition = self._parse_condition(resource)
                    if condition:
                        conditions.append(condition)
            
            return conditions
        except Exception as e:
            print(f"Error getting conditions: {e}")
            return []
    
    def _get_medications(self, patient_id: str) -> List[Medication]:
        """Get patient medications."""
        try:
            bundle = self._make_request(
                'MedicationRequest',
                {'patient': patient_id, 'status': 'active'}
            )
            
            medications = []
            if "entry" in bundle:
                for entry in bundle["entry"]:
                    resource = entry.get("resource", {})
                    medication = self._parse_medication(resource)
                    if medication:
                        medications.append(medication)
            
            return medications
        except Exception as e:
            print(f"Error getting medications: {e}")
            return []
    
    def _get_observations(self, patient_id: str, limit: int = 20) -> List[Observation]:
        """Get recent lab results and vitals."""
        six_months_ago = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
        
        try:
            bundle = self._make_request(
                'Observation',
                {
                    'patient': patient_id,
                    'date': f'ge{six_months_ago}',
                    '_count': limit,
                    '_sort': '-date'
                }
            )
            
            observations = []
            if "entry" in bundle:
                for entry in bundle["entry"]:
                    resource = entry.get("resource", {})
                    observation = self._parse_observation(resource)
                    if observation:
                        observations.append(observation)
            
            return observations
        except Exception as e:
            print(f"Error getting observations: {e}")
            return []
    
    def _get_allergies(self, patient_id: str) -> List[Allergy]:
        """Get patient allergies."""
        try:
            bundle = self._make_request(
                'AllergyIntolerance',
                {'patient': patient_id}
            )
            
            allergies = []
            if "entry" in bundle:
                for entry in bundle["entry"]:
                    resource = entry.get("resource", {})
                    allergy = self._parse_allergy(resource)
                    if allergy:
                        allergies.append(allergy)
            
            return allergies
        except Exception as e:
            print(f"Error getting allergies: {e}")
            return []
    
    def _get_encounters(self, patient_id: str, limit: int = 10) -> List[Encounter]:
        """Get recent patient encounters."""
        try:
            bundle = self._make_request(
                'Encounter',
                {
                    'patient': patient_id,
                    '_count': limit,
                    '_sort': '-date'
                }
            )
            
            encounters = []
            if "entry" in bundle:
                for entry in bundle["entry"]:
                    resource = entry.get("resource", {})
                    encounter = self._parse_encounter(resource)
                    if encounter:
                        encounters.append(encounter)
            
            return encounters
        except Exception as e:
            print(f"Error getting encounters: {e}")
            return []
    
    # Parsing methods (similar to HealthLakeClient)
    def _parse_patient_basic(self, resource: Dict[str, Any]) -> PatientBasic:
        """Parse FHIR Patient resource to PatientBasic."""
        patient_id = resource.get("id", "")
        
        # Parse name
        name = "Unknown"
        if "name" in resource and len(resource["name"]) > 0:
            name_obj = resource["name"][0]
            given = " ".join(name_obj.get("given", []))
            family = name_obj.get("family", "")
            name = f"{given} {family}".strip()
        
        # Parse identifier (MRN)
        mrn = None
        if "identifier" in resource:
            for identifier in resource["identifier"]:
                if identifier.get("use") == "official":
                    mrn = identifier.get("value")
                    break
        
        # Parse birthdate and gender
        dob = resource.get("birthDate")
        gender = resource.get("gender")
        
        return PatientBasic(
            id=patient_id,
            name=name,
            mrn=mrn,
            dob=dob,
            gender=gender
        )
    
    def _parse_condition(self, resource: Dict[str, Any]) -> Optional[Condition]:
        """Parse FHIR Condition resource."""
        code_obj = resource.get("code", {})
        coding = code_obj.get("coding", [])
        
        if not coding:
            return None
        
        code = coding[0].get("code", "")
        display = coding[0].get("display", code)
        clinical_status = resource.get("clinicalStatus", {}).get("coding", [{}])[0].get("code")
        onset_date = resource.get("onsetDateTime", "")
        
        return Condition(
            code=code,
            display=display,
            clinical_status=clinical_status,
            onset_date=onset_date
        )
    
    def _parse_medication(self, resource: Dict[str, Any]) -> Optional[Medication]:
        """Parse FHIR MedicationRequest resource."""
        medication_ref = resource.get("medicationCodeableConcept", {})
        coding = medication_ref.get("coding", [])
        
        if not coding:
            return None
        
        code = coding[0].get("code", "")
        display = coding[0].get("display", code)
        status = resource.get("status", "")
        
        # Parse dosage
        dosage = ""
        if "dosageInstruction" in resource and len(resource["dosageInstruction"]) > 0:
            dosage = resource["dosageInstruction"][0].get("text", "")
        
        return Medication(
            code=code,
            display=display,
            status=status,
            dosage=dosage
        )
    
    def _parse_observation(self, resource: Dict[str, Any]) -> Optional[Observation]:
        """Parse FHIR Observation resource."""
        code_obj = resource.get("code", {})
        coding = code_obj.get("coding", [])
        
        if not coding:
            return None
        
        code = coding[0].get("code", "")
        display = coding[0].get("display", code)
        
        # Parse value
        value = ""
        unit = ""
        if "valueQuantity" in resource:
            value = str(resource["valueQuantity"].get("value", ""))
            unit = resource["valueQuantity"].get("unit", "")
        elif "valueString" in resource:
            value = resource["valueString"]
        
        # Parse date
        date = resource.get("effectiveDateTime", "")
        
        # Check if abnormal
        interpretation = resource.get("interpretation", [])
        abnormal = any(
            interp.get("coding", [{}])[0].get("code") in ["H", "L", "A"]
            for interp in interpretation
        )
        
        return Observation(
            code=code,
            display=display,
            value=value,
            unit=unit,
            date=date,
            abnormal=abnormal
        )
    
    def _parse_allergy(self, resource: Dict[str, Any]) -> Optional[Allergy]:
        """Parse FHIR AllergyIntolerance resource."""
        code_obj = resource.get("code", {})
        coding = code_obj.get("coding", [])
        
        if not coding:
            return None
        
        code = coding[0].get("code", "")
        display = coding[0].get("display", code)
        criticality = resource.get("criticality", "")
        
        # Parse reaction
        reaction = ""
        if "reaction" in resource and len(resource["reaction"]) > 0:
            manifestation = resource["reaction"][0].get("manifestation", [])
            if manifestation:
                reaction = manifestation[0].get("coding", [{}])[0].get("display", "")
        
        return Allergy(
            code=code,
            display=display,
            criticality=criticality,
            reaction=reaction
        )
    
    def _parse_encounter(self, resource: Dict[str, Any]) -> Optional[Encounter]:
        """Parse FHIR Encounter resource."""
        encounter_id = resource.get("id", "")
        
        # Parse type
        encounter_type = ""
        if "type" in resource and len(resource["type"]) > 0:
            type_coding = resource["type"][0].get("coding", [])
            if type_coding:
                encounter_type = type_coding[0].get("display", "")
        
        # Parse period
        date = ""
        if "period" in resource:
            date = resource["period"].get("start", "")
        
        # Parse reason
        reason = ""
        if "reasonCode" in resource and len(resource["reasonCode"]) > 0:
            reason_coding = resource["reasonCode"][0].get("coding", [])
            if reason_coding:
                reason = reason_coding[0].get("display", "")
        
        return Encounter(
            id=encounter_id,
            type=encounter_type,
            date=date,
            reason=reason
        )

