"""
Image analysis endpoint - extracts SceneGraph from images via n8n
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import json
import uuid
from datetime import datetime
import os

from app.settings import settings
from app.services.storage import save_upload
from app.services.n8n_client import analyze_image as n8n_analyze

router = APIRouter()

@router.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    """
    Analyze an uploaded image and extract SceneGraph JSON via n8n.

    Delegates to n8n FIBO analysis workflow for professional image understanding.
    """

    try:
        # Validate file
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")

        # Save upload
        file_path = await save_upload(file)
        upload_id = str(uuid.uuid4())

        if not settings.N8N_ENABLED:
            raise HTTPException(
                status_code=503,
                detail="n8n integration is not enabled"
            )

        # Call n8n analyze workflow
        result = await n8n_analyze(
            image_url=file_path,
            file_name=file.filename or "image.jpg",
            file_size=file.size or 0
        )

        return {
            "upload_id": result.get("upload_id", upload_id),
            "file_path": file_path,
            "file_size": file.size,
            "scene_graph": result.get("scene_graph", {}),
            "message": "Image analyzed via n8n FIBO workflow"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
