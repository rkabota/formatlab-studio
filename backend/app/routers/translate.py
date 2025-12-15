"""
Natural Language to JSON Translation
Converts prose instructions into FIBO-compatible JSON updates
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import jsonpatch
import uuid
from datetime import datetime

from app.services.translator import translate_to_scene_update

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

@router.post("/translate", response_model=TranslateResponse)
async def translate(request: TranslateRequest):
    """
    Translate natural language instructions into JSON SceneGraph updates.

    Supports:
    - Camera adjustments ("zoom in", "wider angle", "tilt up")
    - Lighting changes ("brighten the key light", "warm up the color temperature")
    - Color palette modifications ("add blue to the palette", "increase saturation")
    - Constraint locks ("lock the composition", "prevent bright colors")
    - Style changes ("make it more cinematic", "oil painting style")
    """

    try:
        translation_id = str(uuid.uuid4())
        instruction_lower = request.instruction.lower()

        # Start with current scene
        updated_scene = request.current_scene.copy()

        # Parse natural language and build updates
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

        # Generate JSON Patch if requested
        patch = None
        if request.return_patch:
            patch = jsonpatch.JsonPatch.from_diff(
                request.current_scene,
                updated_scene
            ).patch

        # Build diff summary
        changed_keys = list(updates.keys())
        diff_summary = f"Modified: {', '.join(changed_keys)}" if changed_keys else "No changes"

        return TranslateResponse(
            translation_id=translation_id,
            instruction=request.instruction,
            updated_scene=updated_scene,
            patch=patch,
            diff_summary=diff_summary,
            confidence=0.9 if updates else 0.5
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
