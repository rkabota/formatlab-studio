"""
Image analysis endpoint - extracts SceneGraph from images
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import json
import uuid
from datetime import datetime
import os

from app.settings import settings
from app.services.storage import save_upload

router = APIRouter()

@router.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    """
    Analyze an uploaded image and extract SceneGraph JSON.

    In demo mode: returns a templated SceneGraph
    With FIBO integration: uses actual image understanding to generate SceneGraph
    """

    try:
        # Validate file
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")

        # Save upload
        file_path = await save_upload(file)
        upload_id = str(uuid.uuid4())

        # Generate SceneGraph from image
        # In demo mode, return templated response
        scene_graph = {
            "version": "1.0",
            "id": f"scene_{upload_id[:8]}",
            "timestamp": datetime.now().isoformat(),
            "name": f"Analyzed from {file.filename}",
            "seed": hash(file_path) % 10000,
            "source_image": file_path,
            "subject": {
                "description": "Professional scene with careful composition",
                "style": "photorealistic",
                "position": {
                    "x": 0,
                    "y": 0,
                    "z": 0
                }
            },
            "camera": {
                "lens_mm": 50,
                "fov": 48,
                "angle": 0,
                "tilt": 0,
                "depth_of_field": 0.5
            },
            "lighting": {
                "key": {
                    "angle": 45,
                    "intensity": 0.85,
                    "color": "#FFFFFF",
                    "temperature": 5500
                },
                "fill": {
                    "intensity": 0.35,
                    "angle": 315
                },
                "rim": {
                    "intensity": 0.4,
                    "color": "#FFFFFF"
                },
                "ambient": 0.25
            },
            "color": {
                "palette": ["#1a1a1a", "#4a9eff", "#ffffff", "#e8e8e8"],
                "temperature": 50,
                "saturation": 0.75,
                "contrast": 0.65,
                "vibrance": 0.5
            },
            "constraints": {
                "lock_subject_identity": True,
                "lock_composition": False,
                "lock_palette": False,
                "negative_constraints": ["blurry", "distorted"]
            },
            "metadata": {
                "source_file": file.filename,
                "upload_id": upload_id,
                "analysis_mode": "demo_stub"
            }
        }

        return {
            "upload_id": upload_id,
            "file_path": file_path,
            "file_size": file.size,
            "scene_graph": scene_graph,
            "message": "Image analyzed successfully (demo mode)"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
