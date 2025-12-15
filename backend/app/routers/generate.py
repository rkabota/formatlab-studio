"""
Generate endpoint - calls FIBO or demo generation
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid
import os
import json
from datetime import datetime
from pathlib import Path

from app.settings import settings
from app.services.fibo_client import generate_with_fibo_or_demo

router = APIRouter()

class GenerateRequest(BaseModel):
    base_scene: Dict[str, Any]
    patch: Optional[List[Dict[str, Any]]] = None
    seed: Optional[int] = None
    num_variants: int = 1
    apply_patch: bool = True

@router.post("/generate")
async def generate_images(request: GenerateRequest):
    """
    Generate images from SceneGraph using FIBO API.

    If FIBO API is not available, returns demo placeholder images.
    """

    try:
        run_id = str(uuid.uuid4())

        # Apply patch if provided
        final_scene = request.base_scene.copy()
        if request.patch and request.apply_patch:
            import jsonpatch
            final_scene = jsonpatch.JsonPatch(request.patch).apply(final_scene)

        # Use provided seed or hash scene
        seed = request.seed if request.seed is not None else hash(json.dumps(final_scene, sort_keys=True)) % 100000

        # Generate images
        output_urls = []
        for i in range(request.num_variants):
            variant_seed = seed + i
            # Call FIBO or demo generation
            output_path = await generate_with_fibo_or_demo(
                scene=final_scene,
                seed=variant_seed,
                variant_index=i
            )
            output_urls.append(output_path)

        # Store timeline entry
        timeline_entry = {
            "run_id": run_id,
            "timestamp": datetime.now().isoformat(),
            "seed": seed,
            "base_scene_hash": hash(json.dumps(request.base_scene, sort_keys=True)),
            "patch_count": len(request.patch) if request.patch else 0,
            "output_urls": output_urls,
            "num_variants": request.num_variants
        }

        # Save timeline entry
        timeline_file = os.path.join(settings.STORAGE_DIR, "timeline.jsonl")
        with open(timeline_file, "a") as f:
            f.write(json.dumps(timeline_entry) + "\n")

        return {
            "run_id": run_id,
            "seed": seed,
            "num_variants": request.num_variants,
            "output_urls": output_urls,
            "scene_used": final_scene,
            "timestamp": datetime.now().isoformat(),
            "demo_mode": settings.DEMO_MODE
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
