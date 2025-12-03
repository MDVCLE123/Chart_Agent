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

