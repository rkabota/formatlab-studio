"""
FIBO API Client - Integrates with Bria FIBO for image generation
Uses Bria API V2 with asynchronous processing
"""

import os
import json
import shutil
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import httpx

from app.settings import settings

async def generate_with_fibo_or_demo(
    scene: Dict[str, Any],
    seed: int,
    variant_index: int = 0
) -> str:
    """
    Call FIBO API with SceneGraph JSON, or return demo placeholder.

    In production: would call https://api.bria.ai/fibo
    In demo: returns placeholder from /examples/outputs
    """

    if settings.DEMO_MODE:
        # Return demo placeholder
        return await _generate_demo(scene, seed, variant_index)
    else:
        # Call real FIBO API
        return await _call_fibo_api(scene, seed, variant_index)

async def _call_fibo_api(
    scene: Dict[str, Any],
    seed: int,
    variant_index: int
) -> str:
    """
    Call actual Bria FIBO API for real image generation.
    Uses Bria API V2 with asynchronous processing.

    Flow:
    1. Submit async request to /generate
    2. Get request_id and status_url
    3. Poll /status/{request_id} until COMPLETED
    4. Download image from result.image_url
    """

    if not settings.FIBO_API_KEY:
        print("FIBO_API_KEY not configured, using demo mode")
        return await _generate_demo(scene, seed, variant_index)

    try:
        # Extract scene description for the prompt
        subject_desc = scene.get("subject", {}).get("description", "professional product photo")
        style = scene.get("subject", {}).get("style", "photorealistic")
        camera_lens = scene.get("camera", {}).get("lens_mm", 50)

        # Build prompt from scene
        prompt = f"{subject_desc}, {style}, shot with {camera_lens}mm lens"

        # Prepare Bria API payload
        payload = {
            "prompt": prompt,
            "sync": False,  # Async processing
            "num_images": 1,
            "seed": seed if seed != 0 else None
        }

        # Call Bria FIBO API - Submit async request
        async with httpx.AsyncClient(timeout=30.0) as client:
            submit_response = await client.post(
                f"{settings.FIBO_API_URL}/generate",
                json=payload,
                headers={
                    "api_token": settings.FIBO_API_KEY,
                    "Content-Type": "application/json"
                }
            )

        if submit_response.status_code not in [200, 202]:
            print(f"FIBO submit error: {submit_response.status_code}")
            print(f"Response: {submit_response.text}")
            return await _generate_demo(scene, seed, variant_index)

        result = submit_response.json()
        status_url = result.get("status_url")
        request_id = result.get("request_id")

        if not status_url or not request_id:
            print(f"FIBO didn't return status_url or request_id: {result}")
            return await _generate_demo(scene, seed, variant_index)

        print(f"FIBO request submitted: {request_id}")

        # Poll for completion (with timeout)
        max_polls = 120  # 2 minutes with 1-second intervals
        poll_count = 0

        async with httpx.AsyncClient(timeout=30.0) as client:
            while poll_count < max_polls:
                poll_count += 1

                # Check status
                status_response = await client.get(
                    f"{settings.FIBO_API_URL}/status/{request_id}",
                    headers={"api_token": settings.FIBO_API_KEY}
                )

                if status_response.status_code != 200:
                    print(f"FIBO status check error: {status_response.status_code}")
                    await asyncio.sleep(1)
                    continue

                status_result = status_response.json()
                status = status_result.get("status")

                if status == "COMPLETED":
                    # Get image URL
                    image_url = status_result.get("result", {}).get("image_url")
                    if not image_url:
                        print("FIBO returned COMPLETED but no image_url")
                        return await _generate_demo(scene, seed, variant_index)

                    # Download image
                    image_response = await client.get(image_url, timeout=60.0)
                    if image_response.status_code != 200:
                        print(f"Failed to download image from FIBO: {image_response.status_code}")
                        return await _generate_demo(scene, seed, variant_index)

                    # Save image
                    output_dir = settings.OUTPUTS_DIR
                    os.makedirs(output_dir, exist_ok=True)

                    image_path = os.path.join(
                        output_dir,
                        f"fibo_output_{request_id}_{variant_index}.png"
                    )

                    with open(image_path, "wb") as f:
                        f.write(image_response.content)

                    print(f"✓ Generated image via Bria FIBO: {image_path}")
                    return image_path

                elif status == "ERROR":
                    error = status_result.get("error", {})
                    print(f"FIBO generation error: {error}")
                    return await _generate_demo(scene, seed, variant_index)

                elif status == "IN_PROGRESS":
                    await asyncio.sleep(1)  # Wait before polling again
                else:
                    print(f"FIBO unknown status: {status}")
                    await asyncio.sleep(1)

        # Timeout reached
        print(f"FIBO request {request_id} timed out after {max_polls} seconds")
        return await _generate_demo(scene, seed, variant_index)

    except Exception as e:
        print(f"FIBO API call failed: {str(e)}")
        # Fallback to demo
        return await _generate_demo(scene, seed, variant_index)

async def _generate_demo(
    scene: Dict[str, Any],
    seed: int,
    variant_index: int
) -> str:
    """Generate or return demo placeholder image"""

    output_dir = settings.OUTPUTS_DIR
    os.makedirs(output_dir, exist_ok=True)

    # Generate dummy 512x512 PNG for demo
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        # If PIL not available, create a simple JSON placeholder
        placeholder_path = os.path.join(
            output_dir,
            f"demo_output_{seed}_{variant_index}.json"
        )
        with open(placeholder_path, "w") as f:
            json.dump({
                "generated": True,
                "seed": seed,
                "variant": variant_index,
                "scene": scene.get("name", "Demo Output"),
                "timestamp": datetime.now().isoformat()
            }, f)
        return placeholder_path

    # Create demo image with PIL
    image_path = os.path.join(
        output_dir,
        f"demo_output_{seed}_{variant_index}.png"
    )

    # Create a simple gradient image
    img = Image.new('RGB', (512, 512), color=(20, 20, 20))
    draw = ImageDraw.Draw(img)

    # Add gradient effect
    for y in range(512):
        color_value = int((y / 512) * 200 + 55)
        draw.rectangle(
            [(0, y), (512, y + 1)],
            fill=(color_value, int(color_value * 0.8), 255)
        )

    # Add text overlay
    text = f"FormatLab Studio Demo\nSeed: {seed}\nVariant: {variant_index}"
    draw.text(
        (256, 256),
        text,
        fill=(255, 255, 255),
        anchor="mm"
    )

    img.save(image_path)
    return image_path
