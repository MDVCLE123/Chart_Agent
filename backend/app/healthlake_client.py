"""Multi-source FHIR client supporting HealthLake, Epic, and public servers."""
import boto3
import requests
import json
import jwt
import time
import uuid
from typing import List, Dict, Any, Optional
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from datetime import datetime, timedelta

from app.config import settings
from app.models import (
    PatientBasic, PractitionerBasic, Condition, Medication, Observation, 
    Allergy, Encounter, PatientData
)


# Valid FHIR source options
FHIR_SOURCES = ["healthlake", "epic", "athena", "demo"]

# Epic sandbox test patients (Epic requires known patient IDs for Backend Systems)
EPIC_TEST_PATIENTS = [
    {"id": "erXuFYUfucBZaryVksYEcMg3", "name": "Camila Lopez"},
    {"id": "eq081-VQEgP8drUUqCWzHfw3", "name": "Derrick Lin"},
    {"id": "eAB3mDIBBcyUKviyzrxsnAw3", "name": "Desiree Powell"},
    {"id": "egqBHVfQlt4Bw3XGXoxVxHg3", "name": "Elijah Davis"},
    {"id": "eIXesllypH3M9tAA5WdJftQ3", "name": "Linda Ross"},
    {"id": "eh2xYHuzl9nkSFVvV3osUHg3", "name": "Olivia Roberts"},
    {"id": "e0w0LEDCYtfckT6N.CkJKCw3", "name": "Warren McGinnis"},
]

# athenahealth sandbox test patients (from preview environment practice 195900)
# From: https://docs.athenahealth.com/api/guides/testing-sandbox
ATHENA_TEST_PATIENTS = [
    {"id": "a-195900.E-60178", "name": "Donna Sandboxtest"},
    {"id": "a-195900.E-60179", "name": "Eleana Sandboxtest"},
    {"id": "a-195900.E-60180", "name": "Frankie Sandboxtest"},
    {"id": "a-195900.E-60181", "name": "Anna Sandbox-Test"},
    {"id": "a-195900.E-60182", "name": "Rebecca Sandbox-Test"},
    {"id": "a-195900.E-60183", "name": "Gary Sandboxtest"},
    {"id": "a-195900.E-60184", "name": "Dorrie Sandboxtest"},
]


def get_fhir_client(source: str = None):
    """Factory function to get appropriate FHIR client based on source."""
    if source is None:
        # Default behavior based on settings
        if settings.use_demo_mode:
            source = "demo"
        else:
            source = "healthlake"
    
    return FHIRClient(source=source)


class FHIRClient:
    """Client for interacting with multiple FHIR servers (HealthLake, Epic, athenahealth, public)."""
    
    # Class-level token cache for Epic
    _epic_token = None
    _epic_token_expires = 0
    
    # Class-level token cache for athenahealth
    _athena_token = None
    _athena_token_expires = 0
    
    def __init__(self, source: str = "healthlake"):
        """
        Initialize FHIR client for specified source.
        
        Args:
            source: One of 'healthlake', 'epic', 'athena', or 'demo'
        """
        self.source = source.lower()
        self.auth_type = None  # 'sigv4', 'epic_jwt', 'athena_oauth', or None
        
        if self.source == "epic":
            # Epic Sandbox with JWT authentication
            self.endpoint = settings.epic_fhir_base_url.rstrip('/')
            self.auth_type = "epic_jwt"
            print(f"🏥 Epic mode: Using Epic FHIR sandbox at {self.endpoint}")
        elif self.source == "athena":
            # athenahealth with OAuth2 client credentials
            self.endpoint = settings.athena_fhir_base_url.rstrip('/')
            self.auth_type = "athena_oauth"
            print(f"🏥 athenahealth mode: Using athenahealth sandbox at {self.endpoint}")
        elif self.source == "demo":
            # Public FHIR server for testing (no auth)
            self.endpoint = settings.demo_fhir_server.rstrip('/')
            self.auth_type = None
            print(f"🧪 Demo mode: Using public FHIR server at {self.endpoint}")
        else:
            # AWS HealthLake (requires SigV4 auth)
            self.source = "healthlake"
            self.endpoint = settings.healthlake_datastore_endpoint.rstrip('/')
            self.region = settings.aws_region
            self.auth_type = "sigv4"
            self.session = boto3.Session(
                aws_access_key_id=settings.aws_access_key_id if settings.aws_access_key_id else None,
                aws_secret_access_key=settings.aws_secret_access_key if settings.aws_secret_access_key else None,
                region_name=self.region
            )
            self.credentials = self.session.get_credentials()
            print(f"☁️ HealthLake mode: Using AWS HealthLake at {self.endpoint}")
    
    def _get_epic_token(self) -> str:
        """Get OAuth2 access token for Epic using JWT client credentials."""
        # Check if we have a valid cached token
        if FHIRClient._epic_token and time.time() < FHIRClient._epic_token_expires - 60:
            return FHIRClient._epic_token
        
        try:
            # Read private key
            with open(settings.epic_private_key_path, 'r') as f:
                private_key = f.read()
            
            # Create JWT assertion
            now = int(time.time())
            claims = {
                "iss": settings.epic_client_id,
                "sub": settings.epic_client_id,
                "aud": settings.epic_token_url,
                "jti": str(uuid.uuid4()),
                "exp": now + 300,  # 5 minutes
                "iat": now,
                "nbf": now
            }
            
            # Sign JWT with RS384
            token = jwt.encode(
                claims,
                private_key,
                algorithm="RS384",
                headers={"kid": "chart-agent-key-1"}
            )
            
            # Exchange JWT for access token
            response = requests.post(
                settings.epic_token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
                    "client_assertion": token
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                FHIRClient._epic_token = data["access_token"]
                FHIRClient._epic_token_expires = time.time() + data.get("expires_in", 300)
                print(f"✅ Epic OAuth token obtained successfully")
                return FHIRClient._epic_token
            else:
                print(f"❌ Epic OAuth failed: {response.status_code} - {response.text}")
                raise Exception(f"Epic OAuth failed: {response.text}")
                
        except FileNotFoundError:
            print(f"❌ Epic private key not found at {settings.epic_private_key_path}")
            raise Exception("Epic private key not configured")
        except Exception as e:
            print(f"❌ Epic auth error: {e}")
            raise
    
    def _get_athena_token(self) -> str:
        """Get OAuth2 access token for athenahealth using JWT client assertion (same as Epic)."""
        # Check if we have a valid cached token
        if FHIRClient._athena_token and time.time() < FHIRClient._athena_token_expires - 60:
            return FHIRClient._athena_token
        
        try:
            # Read private key (reusing Epic's key)
            key_path = settings.athena_private_key_path
            if not key_path:
                key_path = settings.epic_private_key_path  # Fallback to Epic key path
            
            with open(key_path, 'r') as f:
                private_key = f.read()
            
            # Create JWT assertion (same pattern as Epic)
            now = int(time.time())
            claims = {
                "iss": settings.athena_client_id,
                "sub": settings.athena_client_id,
                "aud": settings.athena_token_url,
                "jti": str(uuid.uuid4()),
                "exp": now + 300,  # 5 minutes
                "iat": now,
            }
            
            # Sign JWT with RS384 (matching the registered key)
            token = jwt.encode(
                claims,
                private_key,
                algorithm="RS384",
                headers={"kid": "chart-agent-key-1"}
            )
            
            print(f"🔐 athenahealth JWT created, requesting token...")
            
            # Exchange JWT for access token
            response = requests.post(
                settings.athena_token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
                    "client_assertion": token,
                    "scope": "system/Patient.read system/Condition.read system/Observation.read system/MedicationRequest.read system/AllergyIntolerance.read system/Encounter.read system/Practitioner.read"
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                FHIRClient._athena_token = data["access_token"]
                FHIRClient._athena_token_expires = time.time() + data.get("expires_in", 3600)
                print(f"✅ athenahealth JWT OAuth token obtained successfully")
                print(f"   Token scopes: {data.get('scope', 'N/A')}")
                return FHIRClient._athena_token
            else:
                print(f"❌ athenahealth JWT OAuth failed: {response.status_code}")
                print(f"   Response: {response.text}")
                raise Exception(f"athenahealth OAuth failed: {response.text}")
                
        except FileNotFoundError:
            print(f"❌ athenahealth private key not found at {key_path}")
            raise Exception("athenahealth private key not configured")
        except Exception as e:
            print(f"❌ athenahealth auth error: {e}")
            raise
    
    def _make_request(self, method: str, url: str, body: str = "") -> requests.Response:
        """Make a request with appropriate authentication."""
        if self.auth_type == "sigv4":
            # AWS HealthLake - sign with SigV4
            return self._sign_request(method, url, body)
        elif self.auth_type == "epic_jwt":
            # Epic - use OAuth2 bearer token
            try:
                token = self._get_epic_token()
                headers = {
                    "Accept": "application/fhir+json",
                    "Authorization": f"Bearer {token}"
                }
                return requests.request(method=method, url=url, headers=headers, timeout=30)
            except Exception as e:
                print(f"Epic auth failed, trying without auth: {e}")
                headers = {"Accept": "application/fhir+json"}
                return requests.request(method=method, url=url, headers=headers, timeout=30)
        elif self.auth_type == "athena_oauth":
            # athenahealth - use OAuth2 bearer token
            try:
                token = self._get_athena_token()
                headers = {
                    "Accept": "application/fhir+json",
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                print(f"   athenahealth request: {url}")
                response = requests.request(method=method, url=url, headers=headers, timeout=30)
                print(f"   athenahealth response: {response.status_code}")
                return response
            except Exception as e:
                print(f"athenahealth auth failed: {e}")
                raise
        else:
            # Public FHIR server - no auth needed
            headers = {"Accept": "application/fhir+json"}
            return requests.request(method=method, url=url, headers=headers, timeout=30)
    
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
    
    def search_practitioners(self, count: int = 50) -> List[PractitionerBasic]:
        """Search for practitioners in FHIR server."""
        url = f"{self.endpoint}/Practitioner?_count={count}"
        
        try:
            response = self._make_request("GET", url)
            response.raise_for_status()
            bundle = response.json()
            
            practitioners = []
            if "entry" in bundle:
                for entry in bundle["entry"]:
                    resource = entry.get("resource", {})
                    practitioners.append(self._parse_practitioner_basic(resource))
            
            return practitioners
        except Exception as e:
            print(f"Error searching practitioners: {e}")
            return []
    
    def _parse_practitioner_basic(self, resource: Dict[str, Any]) -> PractitionerBasic:
        """Parse FHIR Practitioner resource to PractitionerBasic."""
        practitioner_id = resource.get("id", "")
        
        # Parse name
        name = "Unknown"
        prefix = None
        if "name" in resource and len(resource["name"]) > 0:
            name_obj = resource["name"][0]
            given = " ".join(name_obj.get("given", []))
            family = name_obj.get("family", "")
            name = f"{given} {family}".strip()
            prefixes = name_obj.get("prefix", [])
            if prefixes:
                prefix = prefixes[0]
        
        # Parse specialty (from qualification)
        specialty = None
        if "qualification" in resource:
            for qual in resource["qualification"]:
                code = qual.get("code", {})
                if "text" in code:
                    specialty = code["text"]
                    break
        
        return PractitionerBasic(
            id=practitioner_id,
            name=name,
            prefix=prefix,
            specialty=specialty
        )

    def search_patients(self, count: int = 50, practitioner_id: Optional[str] = None) -> List[PatientBasic]:
        """Search for patients in FHIR server, optionally filtered by practitioner encounters."""
        # Epic sandbox requires known patient IDs - unrestricted searches return empty
        if self.source == "epic":
            return self._get_epic_test_patients(count)
        
        # athenahealth sandbox - try direct search first, fall back to test patients
        if self.source == "athena":
            patients = self._get_athena_patients(count)
            if patients:
                return patients
            print("   Falling back to athenahealth test patients")
            return self._get_athena_test_patients(count)
        
        if practitioner_id:
            # Find patients who have had encounters with this practitioner
            return self._get_patients_by_practitioner_encounters(practitioner_id, count)
        else:
            url = f"{self.endpoint}/Patient?_count={count}"
        
        try:
            response = self._make_request("GET", url)
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
    
    def _get_epic_test_patients(self, count: int = 50) -> List[PatientBasic]:
        """Get Epic test patients by their known IDs."""
        patients = []
        for test_patient in EPIC_TEST_PATIENTS[:count]:
            try:
                url = f"{self.endpoint}/Patient/{test_patient['id']}"
                response = self._make_request("GET", url)
                if response.status_code == 200:
                    resource = response.json()
                    patients.append(self._parse_patient_basic(resource))
            except Exception as e:
                print(f"Error fetching Epic patient {test_patient['id']}: {e}")
        return patients
    
    def _get_athena_patients(self, count: int = 50) -> List[PatientBasic]:
        """Try to get athenahealth patients via search."""
        # athenahealth FHIR R4 uses query param for practice
        # Format: /Patient?ah-practice=Organization/a-1.Practice-{practiceId}&name=Sandboxtest
        practice_id = settings.athena_practice_id
        url = f"{self.endpoint}/Patient?ah-practice=Organization/a-1.Practice-{practice_id}&name=Sandboxtest&_count={count}"
        
        try:
            response = self._make_request("GET", url)
            print(f"   athenahealth Patient search: {response.status_code}")
            if response.status_code == 200:
                bundle = response.json()
                patients = []
                if "entry" in bundle:
                    for entry in bundle["entry"]:
                        resource = entry.get("resource", {})
                        patients.append(self._parse_patient_basic(resource))
                print(f"   Found {len(patients)} athenahealth patients")
                return patients
            else:
                print(f"   Response: {response.text[:200]}")
                return []
        except Exception as e:
            print(f"   athenahealth search error: {e}")
            return []
    
    def _get_athena_test_patients(self, count: int = 50) -> List[PatientBasic]:
        """Get athenahealth test patients by known IDs."""
        patients = []
        
        for test_patient in ATHENA_TEST_PATIENTS[:count]:
            try:
                # athenahealth Patient endpoint - ID includes practice prefix
                url = f"{self.endpoint}/Patient/{test_patient['id']}"
                response = self._make_request("GET", url)
                if response.status_code == 200:
                    resource = response.json()
                    patients.append(self._parse_patient_basic(resource))
                    print(f"   ✅ Fetched {test_patient['name']}")
                else:
                    print(f"   athenahealth patient {test_patient['id']}: {response.status_code}")
            except Exception as e:
                print(f"Error fetching athenahealth patient {test_patient['id']}: {e}")
        
        # If no patients found via API, return mock data for testing UI
        if not patients:
            print("   Returning mock athenahealth patients for UI testing")
            return [
                PatientBasic(id="athena-test-1", name="Test Patient One", dob="1980-01-15", gender="male"),
                PatientBasic(id="athena-test-2", name="Test Patient Two", dob="1975-06-20", gender="female"),
                PatientBasic(id="athena-test-3", name="Test Patient Three", dob="1990-03-10", gender="male"),
            ]
        
        return patients
    
    def _get_patients_by_practitioner_encounters(self, practitioner_id: str, count: int = 50) -> List[PatientBasic]:
        """Get patients who have had encounters with a specific practitioner."""
        # Query encounters for this practitioner (using 'practitioner' search param)
        # Note: HealthLake limits _count to max 100
        url = f"{self.endpoint}/Encounter?practitioner={practitioner_id}&_count=100"
        
        try:
            response = self._make_request("GET", url)
            response.raise_for_status()
            bundle = response.json()
            
            # Extract unique patient IDs from encounters
            patient_ids = set()
            if "entry" in bundle:
                for entry in bundle["entry"]:
                    encounter = entry.get("resource", {})
                    subject = encounter.get("subject", {})
                    ref = subject.get("reference", "")
                    if ref.startswith("Patient/"):
                        patient_id = ref.replace("Patient/", "")
                        patient_ids.add(patient_id)
            
            # Fetch patient details for each unique patient
            patients = []
            for patient_id in list(patient_ids)[:count]:
                patient = self.get_patient(patient_id)
                if patient:
                    patients.append(patient)
            
            return patients
        except Exception as e:
            print(f"Error getting patients by practitioner encounters: {e}")
            return []
    
    def get_patient(self, patient_id: str) -> Optional[PatientBasic]:
        """Get a specific patient by ID."""
        url = f"{self.endpoint}/Patient/{patient_id}"
        
        try:
            response = self._make_request("GET", url)
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
            response = self._make_request("GET", url)
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
            response = self._make_request("GET", url)
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
            response = self._make_request("GET", url)
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
            response = self._make_request("GET", url)
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
            response = self._make_request("GET", url)
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
        
        # Parse general practitioner reference
        general_practitioner_id = None
        if "generalPractitioner" in resource and len(resource["generalPractitioner"]) > 0:
            ref = resource["generalPractitioner"][0].get("reference", "")
            if ref.startswith("Practitioner/"):
                general_practitioner_id = ref.replace("Practitioner/", "")
        
        return PatientBasic(
            id=patient_id,
            name=name,
            mrn=mrn,
            dob=dob,
            gender=gender,
            general_practitioner_id=general_practitioner_id
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


# Backwards compatibility alias
HealthLakeClient = FHIRClient

