"""
Cerebras LLM Translator - Real NL -> JSON translation using Cerebras API
Converts natural language instructions to JSON Patches for SceneGraph
"""

import json
import httpx
from typing import Dict, Any, List, Optional
import asyncio

from app.settings import settings


async def translate_with_cerebras(
    instruction: str,
    current_scene: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Use Cerebras LLM to translate natural language to JSON Patch operations.

    Args:
        instruction: Natural language instruction (e.g., "brighten the key light")
        current_scene: Current SceneGraph JSON

    Returns:
        Dict with: patch, updated_scene, confidence, explanation
    """

    if not settings.CEREBRAS_API_KEY:
        raise ValueError("CEREBRAS_API_KEY not configured")

    # Build system prompt for SceneGraph translation
    system_prompt = """You are an expert at converting natural language instructions into JSON Patch operations for image generation scenes.

You have deep knowledge of:
- Camera settings (lens_mm: 14-300, fov: 10-120, angle, tilt, depth_of_field)
- Lighting (key, fill, rim with intensity: 0-1, angle, color, temperature)
- Color (palette: hex array, temperature: 0-100, saturation: 0-1, contrast: 0-1, vibrance: 0-1)
- Constraints (lock_subject_identity, lock_composition, lock_palette, negative_constraints)

Your task:
1. Parse the user's natural language instruction
2. Identify which SceneGraph properties need to change
3. Generate RFC6902 JSON Patch operations
4. Clamp numeric ranges to valid bounds
5. Return a JSON object with: patch (array), updated_scene (full scene), explanation (string), confidence (0-1)

IMPORTANT: Always output valid RFC6902 JSON Patch format. Each operation must have: op (add/remove/replace/move/copy/test), path (JSON pointer), and value.

Current scene:
{scene_json}

User instruction: {instruction}

Respond ONLY with valid JSON in this format:
{{
    "patch": [...RFC6902 operations...],
    "updated_scene": {{...full updated scene...}},
    "explanation": "Brief description of what changed",
    "confidence": 0.95
}}"""

    try:
        # Prepare the prompt
        prompt = system_prompt.format(
            scene_json=json.dumps(current_scene, indent=2),
            instruction=instruction
        )

        # Call Cerebras API (compatible with OpenAI format)
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{settings.CEREBRAS_API_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.CEREBRAS_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": settings.CEREBRAS_MODEL,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an expert JSON translator for scene graphs. Always respond with valid JSON only."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.3,
                    "max_tokens": 2000
                }
            )

        if response.status_code != 200:
            raise ValueError(f"Cerebras API error: {response.status_code} - {response.text}")

        result = response.json()

        # Extract the response
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

        # Parse JSON response
        parsed = json.loads(content)

        # Validate output
        if not isinstance(parsed.get("patch"), list):
            parsed["patch"] = []

        if not isinstance(parsed.get("updated_scene"), dict):
            parsed["updated_scene"] = current_scene.copy()

        parsed["confidence"] = float(parsed.get("confidence", 0.9))

        return parsed

    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse Cerebras response as JSON: {str(e)}")
    except httpx.HTTPError as e:
        raise ValueError(f"Cerebras API connection error: {str(e)}")
    except Exception as e:
        raise ValueError(f"Cerebras translation failed: {str(e)}")


def validate_patch_for_scene(
    patch: List[Dict[str, Any]],
    scene: Dict[str, Any]
) -> tuple[bool, Optional[str]]:
    """
    Validate that a patch can be safely applied to a scene.

    Args:
        patch: JSON Patch operations
        scene: SceneGraph to validate against

    Returns:
        (is_valid, error_message)
    """
    try:
        import jsonpatch
        jsonpatch.JsonPatch(patch).apply(scene.copy())
        return True, None
    except Exception as e:
        return False, str(e)


async def translate_with_fallback(
    instruction: str,
    current_scene: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Try Cerebras translation first, fall back to rule-based if it fails.

    Args:
        instruction: Natural language instruction
        current_scene: Current SceneGraph

    Returns:
        Translation result with patch and updated_scene
    """

    # Try LLM first if enabled
    if settings.USE_LLM_TRANSLATOR and settings.CEREBRAS_API_KEY:
        try:
            result = await translate_with_cerebras(instruction, current_scene)
            # Validate the patch
            is_valid, error = validate_patch_for_scene(result.get("patch", []), current_scene)
            if is_valid:
                return result
            # If validation fails, fall back
            print(f"LLM patch validation failed: {error}, falling back to rule-based")
        except Exception as e:
            print(f"LLM translation failed: {str(e)}, falling back to rule-based")

    # Fallback to rule-based translation
    from app.routers.translate import translate_with_rules
    return await translate_with_rules(instruction, current_scene)
