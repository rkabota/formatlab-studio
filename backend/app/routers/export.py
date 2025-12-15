"""
Export Bundle endpoint - creates downloadable ZIP with all assets
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import json
import uuid
import zipfile
from datetime import datetime
from io import BytesIO

from app.settings import settings
from app.services.hdr16 import convert_to_16bit

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
    Create an export bundle containing:
    - scene.json (base SceneGraph)
    - patch.json (JSON Patch operations)
    - preview images (8-bit)
    - master.tiff (16-bit HDR)
    """

    try:
        # Create ZIP in memory
        zip_buffer = BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add scene.json
            zip_file.writestr(
                "scene.json",
                json.dumps(request.scene_json, indent=2)
            )

            # Add patch.json if provided
            if request.patch_json:
                zip_file.writestr(
                    "patch.json",
                    json.dumps(request.patch_json, indent=2)
                )

            # Add metadata
            metadata = {
                "export_id": str(uuid.uuid4()),
                "run_id": request.run_id,
                "timestamp": datetime.now().isoformat(),
                "include_16bit": request.include_16bit,
                "scene_name": request.scene_json.get("name", "Untitled Scene"),
                "seed": request.scene_json.get("seed", None)
            }
            zip_file.writestr(
                "metadata.json",
                json.dumps(metadata, indent=2)
            )

            # Add output images if provided
            if request.output_urls:
                for i, url in enumerate(request.output_urls):
                    # In demo mode, these are file paths
                    if os.path.exists(url):
                        zip_file.write(url, arcname=f"preview_{i}.png")

                    # Convert first image to 16-bit if requested
                    if i == 0 and request.include_16bit and os.path.exists(url):
                        try:
                            hdr_path = await convert_to_16bit(url, f"master_16bit.tiff")
                            if os.path.exists(hdr_path):
                                zip_file.write(hdr_path, arcname="master_16bit.tiff")
                        except Exception as e:
                            print(f"Warning: Could not create 16-bit master: {e}")

            # Add example schemas
            schema_dir = os.path.join(os.path.dirname(__file__), "..", "..", "schemas")
            if os.path.exists(schema_dir):
                for schema_file in ["formatlab.scene.schema.json", "formatlab.patch.schema.json"]:
                    schema_path = os.path.join(schema_dir, schema_file)
                    if os.path.exists(schema_path):
                        zip_file.write(schema_path, arcname=f"schemas/{schema_file}")

        # Prepare ZIP for download
        zip_buffer.seek(0)
        filename = f"formatlab_export_{request.run_id[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"

        return FileResponse(
            path=zip_buffer,
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
