"""
Storage service - handles file uploads and organization
"""

import os
import uuid
from fastapi import UploadFile
from app.settings import settings

async def save_upload(file: UploadFile) -> str:
    """Save uploaded file and return path"""

    # Generate unique filename
    file_ext = os.path.splitext(file.filename)[1]
    unique_name = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(settings.UPLOADS_DIR, unique_name)

    # Save file
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    return file_path

def get_output_path(filename: str) -> str:
    """Get output file path"""
    path = os.path.join(settings.OUTPUTS_DIR, filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path

def list_outputs() -> list:
    """List all generated outputs"""
    if not os.path.exists(settings.OUTPUTS_DIR):
        return []
    return [f for f in os.listdir(settings.OUTPUTS_DIR) if f.endswith(('.png', '.jpg', '.tiff'))]
