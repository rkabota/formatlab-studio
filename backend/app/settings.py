"""
Settings and configuration for FormatLab Studio
"""

from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # App
    APP_NAME: str = "FormatLab Studio"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "True") == "True"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # Storage
    STORAGE_DIR: str = "./storage"
    UPLOADS_DIR: str = "./storage/uploads"
    OUTPUTS_DIR: str = "./storage/outputs"

    # FIBO Integration
    FIBO_API_KEY: str = os.getenv("FIBO_API_KEY", "")
    FIBO_API_URL: str = os.getenv("FIBO_API_URL", "https://api.bria.ai/fibo")
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "False") == "True"

    # LLM Integration (Cerebras for NL -> JSON translation)
    CEREBRAS_API_KEY: str = os.getenv("CEREBRAS_API_KEY", "")
    CEREBRAS_API_URL: str = os.getenv("CEREBRAS_API_URL", "https://api.cerebras.ai/v1")
    CEREBRAS_MODEL: str = os.getenv("CEREBRAS_MODEL", "llama-3.3-70b")
    USE_LLM_TRANSLATOR: bool = os.getenv("USE_LLM_TRANSLATOR", "True") == "True"

    # n8n Integration (Workflow Orchestration)
    N8N_ENABLED: bool = os.getenv("N8N_ENABLED", "True") == "True"
    N8N_BASE_URL: str = os.getenv("N8N_BASE_URL", "https://rkabota.app.n8n.cloud")
    N8N_API_KEY: str = os.getenv("N8N_API_KEY", "")
    N8N_WEBHOOK_BASE: str = os.getenv("N8N_WEBHOOK_BASE", "https://rkabota.app.n8n.cloud/webhook")

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Ensure directories exist
os.makedirs(settings.STORAGE_DIR, exist_ok=True)
os.makedirs(settings.UPLOADS_DIR, exist_ok=True)
os.makedirs(settings.OUTPUTS_DIR, exist_ok=True)
