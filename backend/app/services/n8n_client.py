"""
n8n Workflow Client - delegates operations to n8n workflows
"""

import httpx
import asyncio
import json
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
import os

# n8n configuration
N8N_BASE_URL = os.getenv("N8N_BASE_URL", "https://rkabota.app.n8n.cloud")
N8N_API_KEY = os.getenv("N8N_API_KEY", "")
N8N_WEBHOOK_BASE = os.getenv("N8N_WEBHOOK_BASE", f"{N8N_BASE_URL}/webhook")

# API Keys for n8n to use
FIBO_API_KEY = os.getenv("FIBO_API_KEY", "")
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY", "")


async def call_n8n_workflow(
    workflow_name: str,
    payload: Dict[str, Any],
    timeout: int = 300
) -> Dict[str, Any]:
    """
    Call an n8n workflow via webhook.

    Args:
        workflow_name: Name of workflow (analyze, translate, generate, export)
        payload: Data to send to workflow
        timeout: Request timeout in seconds

    Returns:
        Response from workflow
    """

    webhook_url = f"{N8N_WEBHOOK_BASE}/{workflow_name}"

    # Add API keys to payload for n8n to use
    payload = {
        **payload,
        "_api_keys": {
            "FIBO_API_KEY": FIBO_API_KEY,
            "CEREBRAS_API_KEY": CEREBRAS_API_KEY
        }
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                webhook_url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                }
            )

            if response.status_code >= 400:
                raise Exception(
                    f"n8n workflow error: {response.status_code} - {response.text}"
                )

            return response.json()

    except asyncio.TimeoutError:
        raise Exception(f"n8n workflow timeout for {workflow_name}")
    except Exception as e:
        raise Exception(f"Failed to call n8n workflow {workflow_name}: {str(e)}")


async def analyze_image(
    image_url: str,
    file_name: str = "image.jpg",
    file_size: int = 0
) -> Dict[str, Any]:
    """
    Analyze image via n8n FIBO workflow.

    Args:
        image_url: URL of image to analyze
        file_name: Original filename
        file_size: File size in bytes

    Returns:
        {upload_id, scene_graph, ...}
    """

    payload = {
        "image_url": image_url,
        "file_name": file_name,
        "file_size": file_size
    }

    return await call_n8n_workflow("analyze", payload, timeout=60)


async def translate_instruction(
    instruction: str,
    current_scene: Dict[str, Any],
    return_patch: bool = True
) -> Dict[str, Any]:
    """
    Translate natural language to JSON Patch via n8n Cerebras workflow.

    Args:
        instruction: Natural language instruction
        current_scene: Current SceneGraph JSON
        return_patch: Whether to return patch operations

    Returns:
        {translation_id, patch, updated_scene, confidence, ...}
    """

    payload = {
        "instruction": instruction,
        "current_scene": current_scene,
        "return_patch": return_patch
    }

    return await call_n8n_workflow("translate", payload, timeout=30)


async def generate_images(
    base_scene: Dict[str, Any],
    seed: Optional[int] = None,
    num_variants: int = 1,
    patch: Optional[List[Dict[str, Any]]] = None,
    apply_patch: bool = True
) -> Dict[str, Any]:
    """
    Generate images via n8n FIBO workflow.

    Args:
        base_scene: Base SceneGraph JSON
        seed: Random seed for reproducibility
        num_variants: Number of variant images to generate
        patch: Optional JSON Patch to apply first
        apply_patch: Whether to apply patch before generation

    Returns:
        {run_id, seed, output_urls, scene_used, ...}
    """

    # Apply patch if provided
    final_scene = base_scene.copy()
    if patch and apply_patch:
        try:
            import jsonpatch
            final_scene = jsonpatch.JsonPatch(patch).apply(final_scene)
        except Exception as e:
            print(f"Warning: Could not apply patch: {e}")

    payload = {
        "base_scene": final_scene,
        "seed": seed or hash(json.dumps(final_scene, sort_keys=True)) % 100000,
        "num_variants": num_variants,
        "patch": patch,
        "apply_patch": apply_patch
    }

    # FIBO generation can take a while - extend timeout
    return await call_n8n_workflow("generate", payload, timeout=180)


async def export_bundle(
    run_id: str,
    scene_json: Dict[str, Any],
    patch_json: Optional[List[Dict[str, Any]]] = None,
    output_urls: Optional[List[str]] = None,
    include_16bit: bool = True
) -> Dict[str, Any]:
    """
    Export scene as ZIP bundle via n8n workflow.

    Args:
        run_id: Run identifier
        scene_json: SceneGraph JSON
        patch_json: JSON Patch operations
        output_urls: Generated image URLs
        include_16bit: Whether to include 16-bit masters

    Returns:
        {export_id, zip_base64, filename, ...}
    """

    payload = {
        "run_id": run_id,
        "scene_json": scene_json,
        "patch_json": patch_json,
        "output_urls": output_urls or [],
        "include_16bit": include_16bit
    }

    return await call_n8n_workflow("export", payload, timeout=60)


async def check_n8n_status() -> Dict[str, Any]:
    """
    Check if n8n is accessible and workflows are configured.

    Returns:
        {status, n8n_url, workflows_available, ...}
    """

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            # Try health endpoint
            response = await client.get(f"{N8N_BASE_URL}/api/v1/workflows")

            return {
                "status": "ok",
                "n8n_url": N8N_BASE_URL,
                "accessible": True,
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        return {
            "status": "error",
            "n8n_url": N8N_BASE_URL,
            "accessible": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
