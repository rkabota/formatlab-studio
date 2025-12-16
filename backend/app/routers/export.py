"""
Export Bundle endpoint - creates downloadable ZIP via n8n
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import json
import uuid
import zipfile
from datetime import datetime
from io import BytesIO
import base64

from app.settings import settings
from app.services.n8n_client import export_bundle as n8n_export

router = APIRouter()

class ExportRequest(BaseModel):
    run_id: str
    scene_json: Dict[str, Any]
    patch_json: Optional[List[Dict[str, Any]]] = None
    output_urls: Optional[List[str]] = None
    include_16bit: bool = True

@router.post("/export")
async def export_bundle(request: ExportRequest):
    """
    Create an export bundle via n8n containing:
    - scene.json (base SceneGraph)
    - patch.json (JSON Patch operations)
    - preview images (8-bit)
    - master.tiff (16-bit HDR)
    """

    try:
        if not settings.N8N_ENABLED:
            raise HTTPException(
                status_code=503,
                detail="n8n integration is not enabled"
            )

        # Call n8n export workflow
        result = await n8n_export(
            run_id=request.run_id,
            scene_json=request.scene_json,
            patch_json=request.patch_json,
            output_urls=request.output_urls,
            include_16bit=request.include_16bit
        )

        # Extract ZIP from result
        zip_base64 = result.get("zip_base64", "")
        filename = result.get("filename", f"formatlab_export_{request.run_id[:8]}.zip")

        if not zip_base64:
            raise HTTPException(
                status_code=500,
                detail="n8n workflow did not return ZIP data"
            )

        # Decode base64 ZIP
        zip_data = base64.b64decode(zip_base64)

        return StreamingResponse(
            iter([zip_data]),
            media_type="application/zip",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/{run_id}")
async def get_export_info(run_id: str):
    """Get information about a previous export"""
    try:
        # This would query timeline storage
        return {
            "run_id": run_id,
            "message": "Export information not yet available",
            "available_exports": []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
