from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Application settings."""
    
    # App settings
    app_name: str = Field(default="FastAPI Scraper", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    
    # Server settings
    host: str = Field(default="127.0.0.1", description="Server host")
    port: int = Field(default=8000, description="Server port")
    
    # API settings
    api_prefix: str = Field(default="/api/v1", description="API prefix")
    
    # FireCrawl settings
    firecrawl_api_key: str = Field(..., description="FireCrawl API key")
    firecrawl_base_url: Optional[str] = Field(default=None, description="FireCrawl base URL")
    
    # Rate limiting
    rate_limit_requests: int = Field(default=100, description="Rate limit requests per minute")
    rate_limit_window: int = Field(default=60, description="Rate limit window in seconds")
    
    # CORS settings
    cors_origins: list[str] = Field(default=["*"], description="CORS origins")
    cors_methods: list[str] = Field(default=["GET", "POST", "PUT", "DELETE"], description="CORS methods")
    cors_headers: list[str] = Field(default=["*"], description="CORS headers")
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", description="Log format")
    
    # Job settings
    job_timeout: int = Field(default=300, description="Job timeout in seconds")
    max_concurrent_jobs: int = Field(default=10, description="Maximum concurrent jobs")
    
    # Storage settings (for future use)
    storage_path: str = Field(default="./storage", description="Storage path for files")
    
    class Config:
        env_file = ".env"
        env_prefix = "SCRAPER_"
        case_sensitive = False

# Global settings instance
settings = Settings()

# Ensure storage directory exists
Path(settings.storage_path).mkdir(parents=True, exist_ok=True) 