"""
JSON Patch Service - Apply RFC6902 patches to SceneGraph JSON
"""

from typing import Dict, Any, List
import jsonpatch
import copy


def apply_patch(base_scene: Dict[str, Any], patch_ops: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Apply JSON Patch operations to a SceneGraph.

    Args:
        base_scene: Original SceneGraph to patch
        patch_ops: List of RFC6902 patch operations

    Returns:
        Modified SceneGraph with patch applied
    """
    try:
        if not patch_ops:
            return copy.deepcopy(base_scene)

        result = jsonpatch.JsonPatch(patch_ops).apply(base_scene)
        return result
    except Exception as e:
        raise ValueError(f"Failed to apply patch: {str(e)}")


def generate_patch(original: Dict[str, Any], modified: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate JSON Patch operations between two SceneGraphs.

    Args:
        original: Original SceneGraph
        modified: Modified SceneGraph

    Returns:
        List of RFC6902 patch operations
    """
    try:
        patch = jsonpatch.JsonPatch.from_diff(original, modified)
        return patch.patch
    except Exception as e:
        raise ValueError(f"Failed to generate patch: {str(e)}")


def validate_patch_operations(patch_ops: List[Dict[str, Any]]) -> bool:
    """
    Validate that patch operations are well-formed.

    Args:
        patch_ops: List of RFC6902 patch operations

    Returns:
        True if valid, raises exception otherwise
    """
    required_fields = {"op", "path"}
    valid_ops = {"add", "remove", "replace", "move", "copy", "test"}

    for op in patch_ops:
        if not isinstance(op, dict):
            raise ValueError(f"Patch operation must be dict, got {type(op)}")

        if not required_fields.issubset(op.keys()):
            raise ValueError(f"Patch operation missing required fields: {required_fields}")

        if op.get("op") not in valid_ops:
            raise ValueError(f"Invalid patch operation: {op.get('op')}")

        if not isinstance(op.get("path"), str):
            raise ValueError(f"Patch path must be string, got {type(op.get('path'))}")

    return True


def merge_patches(patch1: List[Dict[str, Any]], patch2: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Combine two patch operations into a single patch.

    Args:
        patch1: First set of patch operations
        patch2: Second set of patch operations

    Returns:
        Combined patch operations
    """
    # Simply concatenate - order matters for patch application
    return patch1 + patch2


def get_modified_paths(patch_ops: List[Dict[str, Any]]) -> List[str]:
    """
    Extract which paths were modified by a patch.

    Args:
        patch_ops: List of RFC6902 patch operations

    Returns:
        List of JSON paths that were modified
    """
    paths = []
    for op in patch_ops:
        path = op.get("path", "")
        if path and path not in paths:
            # Extract top-level key from path (e.g., "/camera/lens_mm" -> "camera")
            key = path.split("/")[1] if path.startswith("/") else path.split("/")[0]
            if key and key not in paths:
                paths.append(key)
    return paths
