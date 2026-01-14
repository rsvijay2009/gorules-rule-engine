"""
Application Configuration

Centralized configuration using Pydantic Settings
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    
    # Application
    APP_NAME: str = "BRE Platform"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"  # development, staging, production
    DEBUG: bool = False
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    # Rules
    RULES_SOURCE: str = "git"  # git, local, api
    RULES_DIRECTORY: str = "rules"
    GIT_REPO_URL: Optional[str] = None
    GIT_BRANCH: str = "main"
    GIT_TOKEN: Optional[str] = None
    RULES_REFRESH_INTERVAL: int = 60  # seconds
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/bre_platform"
    
    # Audit
    AUDIT_ENABLED: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Security
    SECRET_KEY: str = "change-this-secret-key-in-production"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
