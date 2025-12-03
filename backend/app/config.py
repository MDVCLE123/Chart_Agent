"""Application configuration."""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings."""
    
    # AWS Configuration
    aws_region: str = "us-east-1"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    
    # HealthLake Configuration
    healthlake_datastore_endpoint: str = ""
    
    # Demo Mode - Use public FHIR server for testing
    use_demo_mode: bool = True  # Set to False to use HealthLake
    demo_fhir_server: str = "https://hapi.fhir.org/baseR4"
    
    # Epic FHIR Configuration
    epic_fhir_base_url: str = "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4"
    epic_client_id: str = "5f2384c3-5bb4-484f-a528-068177894d81"  # Non-Production Client ID
    epic_token_url: str = "https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token"
    epic_private_key_path: str = "/app/keys/epic_private_key.pem"
    
    # athenahealth FHIR Configuration
    athena_fhir_base_url: str = "https://api.preview.platform.athenahealth.com/fhir/r4"
    athena_client_id: str = "0oa1048xe2u6ejB4j298"
    athena_client_secret: str = "8pVwAzKNfIkPnWKguK5esYocO_y-NJG9VQNICHnLww8ZhO7YT9TeafPO5-ucS-fT"
    athena_token_url: str = "https://api.preview.platform.athenahealth.com/oauth2/v1/token"
    
    # Bedrock Configuration
    bedrock_model_id: str = "us.anthropic.claude-sonnet-4-20250514-v1:0"
    
    # Application Configuration
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    
    # CORS Configuration
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

