"""AWS HealthLake FHIR client."""
import boto3
import requests
import json
from typing import List, Dict, Any, Optional
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from datetime import datetime, timedelta

from app.config import settings
from app.models import (
    PatientBasic, Condition, Medication, Observation, 
    Allergy, Encounter, PatientData
)


class HealthLakeClient:
    """Client for interacting with AWS HealthLake FHIR API."""
    
    def __init__(self):
        self.endpoint = settings.healthlake_datastore_endpoint.rstrip('/')
        self.region = settings.aws_region
        self.session = boto3.Session(
            aws_access_key_id=settings.aws_access_key_id if settings.aws_access_key_id else None,
            aws_secret_access_key=settings.aws_secret_access_key if settings.aws_secret_access_key else None,
            region_name=self.region
        )
        self.credentials = self.session.get_credentials()
    
    def _sign_request(self, method: str, url: str, body: str = "") -> requests.Response:
        """Sign request with AWS SigV4 and execute."""
        request = AWSRequest(method=method, url=url, data=body)
        SigV4Auth(self.credentials, "healthlake", self.region).add_auth(request)
        
        return requests.request(
            method=request.method,
            url=request.url,
            headers=dict(request.headers),
            data=request.body
        )
    
    def search_patients(self, count: int = 50) -> List[PatientBasic]:
        """Search for patients in HealthLake."""
        url = f"{self.endpoint}/Patient?_count={count}"
        
        try:
            response = self._sign_request("GET", url)
            response.raise_for_status()
            bundle = response.json()
            
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
        url = f"{self.endpoint}/Patient/{patient_id}"
        
        try:
            response = self._sign_request("GET", url)
            response.raise_for_status()
            resource = response.json()
            return self._parse_patient_basic(resource)
        except Exception as e:
            print(f"Error getting patient {patient_id}: {e}")
            return None
    
    def get_patient_data(self, patient_id: str) -> PatientData:
        """Fetch all relevant data for a patient."""
        patient = self.get_patient(patient_id)
        if not patient:
            raise ValueError(f"Patient {patient_id} not found")
        
        # Fetch all resources in parallel (simplified sequential for now)
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
        url = f"{self.endpoint}/Condition?patient={patient_id}&clinical-status=active"
        
        try:
            response = self._sign_request("GET", url)
            response.raise_for_status()
            bundle = response.json()
            
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
        url = f"{self.endpoint}/MedicationStatement?patient={patient_id}&status=active"
        
        try:
            response = self._sign_request("GET", url)
            response.raise_for_status()
            bundle = response.json()
            
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
        # Get observations from last 6 months
        six_months_ago = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
        url = f"{self.endpoint}/Observation?patient={patient_id}&date=ge{six_months_ago}&_count={limit}&_sort=-date"
        
        try:
            response = self._sign_request("GET", url)
            response.raise_for_status()
            bundle = response.json()
            
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
        url = f"{self.endpoint}/AllergyIntolerance?patient={patient_id}"
        
        try:
            response = self._sign_request("GET", url)
            response.raise_for_status()
            bundle = response.json()
            
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
        url = f"{self.endpoint}/Encounter?patient={patient_id}&_count={limit}&_sort=-date"
        
        try:
            response = self._sign_request("GET", url)
            response.raise_for_status()
            bundle = response.json()
            
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
                if identifier.get("system") == "urn:oid:1.2.36.146.595.217.0.1":
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
        """Parse FHIR MedicationStatement resource."""
        medication_ref = resource.get("medicationCodeableConcept", {})
        coding = medication_ref.get("coding", [])
        
        if not coding:
            return None
        
        code = coding[0].get("code", "")
        display = coding[0].get("display", code)
        status = resource.get("status", "")
        
        # Parse dosage
        dosage = ""
        if "dosage" in resource and len(resource["dosage"]) > 0:
            dosage = resource["dosage"][0].get("text", "")
        
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

