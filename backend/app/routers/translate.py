"""
Natural Language to JSON Translation via n8n
Converts prose instructions into FIBO-compatible JSON updates using Cerebras LLM
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import jsonpatch
import uuid
from datetime import datetime

from app.settings import settings
from app.services.n8n_client import translate_instruction as n8n_translate

router = APIRouter()

class TranslateRequest(BaseModel):
    instruction: str
    current_scene: Dict[str, Any]
    return_patch: bool = True

class TranslateResponse(BaseModel):
    translation_id: str
    instruction: str
    updated_scene: Dict[str, Any]
    patch: Optional[List[Dict[str, Any]]] = None
    diff_summary: str
    confidence: float = 0.95

async def translate_with_rules(
    instruction: str,
    current_scene: Dict[str, Any]
) -> Dict[str, Any]:
    """Rule-based translation fallback"""
    instruction_lower = instruction.lower()
    updated_scene = current_scene.copy()
    updates = {}

    # Camera adjustments
    if any(word in instruction_lower for word in ["zoom", "closer", "tighter"]):
        updates["camera"] = updates.get("camera", {})
        updates["camera"]["lens_mm"] = 100
    elif any(word in instruction_lower for word in ["wider", "pull back", "zoom out"]):
        updates["camera"] = updates.get("camera", {})
        updates["camera"]["lens_mm"] = 35
    elif any(word in instruction_lower for word in ["angle", "tilt", "down"]):
        updates["camera"] = updates.get("camera", {})
        updates["camera"]["tilt"] = -15

    # Lighting adjustments
    if any(word in instruction_lower for word in ["brighten", "increase light", "more light"]):
        updates["lighting"] = updates.get("lighting", {})
        updates["lighting"]["key"] = updates["lighting"].get("key", {})
        updates["lighting"]["key"]["intensity"] = 0.95
    elif any(word in instruction_lower for word in ["darken", "decrease light", "less light"]):
        updates["lighting"] = updates.get("lighting", {})
        updates["lighting"]["key"] = updates["lighting"].get("key", {})
        updates["lighting"]["key"]["intensity"] = 0.65

    # Color temperature
    if any(word in instruction_lower for word in ["warm", "warmer"]):
        updates["color"] = updates.get("color", {})
        updates["color"]["temperature"] = 75
    elif any(word in instruction_lower for word in ["cool", "cooler", "cold"]):
        updates["color"] = updates.get("color", {})
        updates["color"]["temperature"] = 30

    # Saturation
    if any(word in instruction_lower for word in ["saturate", "vivid", "vibrant", "saturated"]):
        updates["color"] = updates.get("color", {})
        updates["color"]["saturation"] = 0.95
    elif any(word in instruction_lower for word in ["desaturate", "muted", "less color"]):
        updates["color"] = updates.get("color", {})
        updates["color"]["saturation"] = 0.4

    # Contrast
    if any(word in instruction_lower for word in ["contrast", "punchy", "crisp"]):
        updates["color"] = updates.get("color", {})
        updates["color"]["contrast"] = 0.85

    # Depth of field
    if any(word in instruction_lower for word in ["blur background", "shallow focus", "separation"]):
        updates["camera"] = updates.get("camera", {})
        updates["camera"]["depth_of_field"] = 0.9
    elif any(word in instruction_lower for word in ["sharp", "deep focus"]):
        updates["camera"] = updates.get("camera", {})
        updates["camera"]["depth_of_field"] = 0.2

    # Locks / constraints
    if "lock" in instruction_lower and "composition" in instruction_lower:
        updates["constraints"] = updates.get("constraints", {})
        updates["constraints"]["lock_composition"] = True
    if "lock" in instruction_lower and "subject" in instruction_lower:
        updates["constraints"] = updates.get("constraints", {})
        updates["constraints"]["lock_subject_identity"] = True

    # Deep merge updates into scene
    for key, value in updates.items():
        if isinstance(value, dict) and key in updated_scene and isinstance(updated_scene[key], dict):
            updated_scene[key].update(value)
        else:
            updated_scene[key] = value

    # Generate JSON Patch
    patch = jsonpatch.JsonPatch.from_diff(
        current_scene,
        updated_scene
    ).patch

    # Build diff summary
    changed_keys = list(updates.keys())
    diff_summary = f"Modified: {', '.join(changed_keys)}" if changed_keys else "No changes"

    return {
        "patch": patch,
        "updated_scene": updated_scene,
        "diff_summary": diff_summary,
        "confidence": 0.9 if updates else 0.5,
        "explanation": f"Rule-based translation: {diff_summary}"
    }


@router.post("/translate", response_model=TranslateResponse)
async def translate(request: TranslateRequest):
    """
    Translate natural language instructions into JSON SceneGraph updates via n8n.

    Uses Cerebras LLM through n8n workflow for professional JSON Patch generation.

    Supports:
    - Camera adjustments ("zoom in", "wider angle", "tilt up")
    - Lighting changes ("brighten the key light", "warm up the color temperature")
    - Color palette modifications ("increase saturation", "add warmth")
    - Constraint locks ("lock the composition", "prevent bright colors")
    - Style changes ("more cinematic", "dramatic lighting")
    """

    try:
        if not settings.N8N_ENABLED:
            raise HTTPException(
                status_code=503,
                detail="n8n integration is not enabled"
            )

        translation_id = str(uuid.uuid4())

        # Call n8n translate workflow
        result = await n8n_translate(
            instruction=request.instruction,
            current_scene=request.current_scene,
            return_patch=request.return_patch
        )

        # Extract patch if requested
        patch = result.get("patch") if request.return_patch else None

        return TranslateResponse(
            translation_id=result.get("translation_id", translation_id),
            instruction=request.instruction,
            updated_scene=result.get("updated_scene", request.current_scene),
            patch=patch,
            diff_summary=result.get("reasoning", "Translation via Cerebras LLM"),
            confidence=result.get("confidence", 0.85)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
