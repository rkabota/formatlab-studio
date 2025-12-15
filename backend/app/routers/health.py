"""
Health check endpoint
"""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "ok",
        "app": "FormatLab Studio",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "environment": "demo_mode"
    }
