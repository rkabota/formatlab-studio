"""
Generate endpoint - calls FIBO via n8n for image generation
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
from app.services.n8n_client import generate_images as n8n_generate

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
    Generate images from SceneGraph using FIBO API via n8n.

    Delegates to n8n FIBO generation workflow for async image generation with polling.
    """

    try:
        if not settings.N8N_ENABLED:
            raise HTTPException(
                status_code=503,
                detail="n8n integration is not enabled"
            )

        # Use provided seed or hash scene
        seed = request.seed if request.seed is not None else hash(json.dumps(request.base_scene, sort_keys=True)) % 100000

        # Call n8n generate workflow
        result = await n8n_generate(
            base_scene=request.base_scene,
            seed=seed,
            num_variants=request.num_variants,
            patch=request.patch,
            apply_patch=request.apply_patch
        )

        # Extract run_id and output URLs
        run_id = result.get("run_id", str(uuid.uuid4()))
        output_urls = result.get("output_urls", [])
        final_scene = result.get("scene_used", request.base_scene)

        # Store timeline entry
        timeline_entry = {
            "run_id": run_id,
            "timestamp": datetime.now().isoformat(),
            "seed": seed,
            "base_scene_hash": hash(json.dumps(request.base_scene, sort_keys=True)),
            "patch_count": len(request.patch) if request.patch else 0,
            "output_urls": output_urls,
            "num_variants": request.num_variants,
            "status": "completed"
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
            "via_n8n": True
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
