"""
FIBO API Client - Integrates with Bria FIBO for image generation
"""

import os
import json
import shutil
from typing import Dict, Any
from datetime import datetime
from pathlib import Path

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
    """Call actual FIBO API for real image generation"""

    try:
        import httpx
    except ImportError:
        # Fallback if httpx not available
        return await _generate_demo(scene, seed, variant_index)

    try:
        # Prepare FIBO API payload
        # FIBO expects SceneGraph JSON + generation parameters
        payload = {
            "scene_graph": scene,
            "seed": seed,
            "num_variants": 1,
            "output_format": "png"
        }

        # Call FIBO API
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{settings.FIBO_API_URL}/generate",
                json=payload,
                headers={
                    "Authorization": f"Bearer {settings.FIBO_API_KEY}",
                    "Content-Type": "application/json"
                }
            )

        if response.status_code != 200:
            print(f"FIBO API error: {response.status_code}")
            print(f"Response: {response.text}")
            return await _generate_demo(scene, seed, variant_index)

        result = response.json()

        # Extract image from response
        # FIBO returns image bytes or URL
        image_data = result.get("output", {}).get("images", [{}])[0].get("data")
        if not image_data:
            return await _generate_demo(scene, seed, variant_index)

        # Save image
        import base64
        output_dir = settings.OUTPUTS_DIR
        os.makedirs(output_dir, exist_ok=True)

        image_path = os.path.join(
            output_dir,
            f"fibo_output_{seed}_{variant_index}.png"
        )

        # Decode and save image
        image_bytes = base64.b64decode(image_data)
        with open(image_path, "wb") as f:
            f.write(image_bytes)

        print(f"✓ Generated image via FIBO: {image_path}")
        return image_path

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
