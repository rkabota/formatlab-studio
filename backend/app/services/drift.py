"""
Drift Meter - Calculate how much a scene has changed from original
"""

from typing import Dict, Any, List, Tuple
import json
from collections.abc import Mapping


def calculate_drift_score(original: Dict[str, Any], modified: Dict[str, Any]) -> float:
    """
    Calculate a drift score (0-1) indicating how much a scene has changed.

    Score calculation:
    - 0 = no changes
    - 1 = complete replacement
    - Values in between represent partial modifications

    Args:
        original: Original SceneGraph
        modified: Modified SceneGraph

    Returns:
        Drift score from 0.0 to 1.0
    """
    if original == modified:
        return 0.0

    # Count modified keys
    modified_keys = get_modified_keys(original, modified)
    if not modified_keys:
        return 0.0

    # Calculate percentage of keys that changed
    all_keys = get_all_keys(original) | get_all_keys(modified)
    if not all_keys:
        return 0.0

    score = len(modified_keys) / len(all_keys)
    return min(1.0, score)


def get_modified_keys(original: Dict[str, Any], modified: Dict[str, Any]) -> set:
    """
    Find all keys that were modified between two objects.

    Args:
        original: Original object
        modified: Modified object

    Returns:
        Set of key paths that were modified
    """
    modified = set()

    # Check top-level keys
    all_keys = set(original.keys()) | set(modified.keys())

    for key in all_keys:
        orig_val = original.get(key)
        mod_val = modified.get(key)

        if orig_val != mod_val:
            if isinstance(orig_val, dict) and isinstance(mod_val, dict):
                # Recursively check nested dicts
                sub_modified = get_modified_keys(orig_val, mod_val)
                for sub_key in sub_modified:
                    modified.add(f"{key}.{sub_key}")
            else:
                modified.add(key)

    return modified


def get_all_keys(obj: Dict[str, Any], prefix: str = "") -> set:
    """
    Get all keys in an object, including nested keys.

    Args:
        obj: Object to analyze
        prefix: Prefix for nested keys

    Returns:
        Set of all key paths
    """
    keys = set()

    for key, value in obj.items():
        full_key = f"{prefix}.{key}" if prefix else key
        keys.add(full_key)

        if isinstance(value, dict):
            keys.update(get_all_keys(value, full_key))

    return keys


def get_numeric_differences(
    original: Dict[str, Any], modified: Dict[str, Any]
) -> Dict[str, Tuple[float, float]]:
    """
    Find all numeric values that changed and their delta.

    Args:
        original: Original SceneGraph
        modified: Modified SceneGraph

    Returns:
        Dict mapping changed numeric keys to (original_value, new_value) tuples
    """
    differences = {}

    def compare_recursively(orig, mod, path=""):
        if isinstance(orig, dict) and isinstance(mod, dict):
            for key in set(orig.keys()) | set(mod.keys()):
                new_path = f"{path}/{key}" if path else key
                orig_val = orig.get(key)
                mod_val = mod.get(key)

                if isinstance(orig_val, (int, float)) and isinstance(mod_val, (int, float)):
                    if orig_val != mod_val:
                        differences[new_path] = (orig_val, mod_val)
                elif isinstance(orig_val, dict) and isinstance(mod_val, dict):
                    compare_recursively(orig_val, mod_val, new_path)

    compare_recursively(original, modified)
    return differences


def get_impact_summary(
    original: Dict[str, Any], modified: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Get a detailed summary of what changed.

    Args:
        original: Original SceneGraph
        modified: Modified SceneGraph

    Returns:
        Dictionary with change summary
    """
    modified_keys = get_modified_keys(original, modified)
    numeric_diffs = get_numeric_differences(original, modified)

    # Categorize changes by domain
    camera_changes = [k for k in modified_keys if k.startswith("camera")]
    lighting_changes = [k for k in modified_keys if k.startswith("lighting")]
    color_changes = [k for k in modified_keys if k.startswith("color")]
    constraint_changes = [k for k in modified_keys if k.startswith("constraint")]
    other_changes = [
        k
        for k in modified_keys
        if not any(
            k.startswith(prefix)
            for prefix in ["camera", "lighting", "color", "constraint"]
        )
    ]

    return {
        "drift_score": calculate_drift_score(original, modified),
        "total_changes": len(modified_keys),
        "modified_keys": list(modified_keys),
        "numeric_differences": numeric_diffs,
        "changes_by_domain": {
            "camera": camera_changes,
            "lighting": lighting_changes,
            "color": color_changes,
            "constraints": constraint_changes,
            "other": other_changes,
        },
        "summary": f"Modified {len(camera_changes)} camera settings, {len(lighting_changes)} lighting settings, {len(color_changes)} color settings"
        if modified_keys
        else "No changes detected",
    }


def check_constraint_violations(
    original: Dict[str, Any], modified: Dict[str, Any]
) -> List[str]:
    """
    Check if any locked constraints were violated.

    Args:
        original: Original SceneGraph with constraints
        modified: Modified SceneGraph

    Returns:
        List of constraint violations (empty if none)
    """
    violations = []
    constraints = original.get("constraints", {})

    # Check if subject identity was locked but changed
    if constraints.get("lock_subject", False):
        if original.get("subject") != modified.get("subject"):
            violations.append("Subject identity was locked but was modified")

    # Check if composition was locked but changed
    if constraints.get("lock_composition", False):
        orig_camera = original.get("camera", {})
        mod_camera = modified.get("camera", {})
        if orig_camera != mod_camera:
            violations.append("Composition was locked but camera settings changed")

    # Check if palette was locked but changed
    if constraints.get("lock_palette", False):
        orig_color = original.get("color", {})
        mod_color = modified.get("color", {})
        if orig_color.get("palette") != mod_color.get("palette"):
            violations.append("Palette was locked but was modified")

    return violations


def calculate_bounded_drift(
    original: Dict[str, Any],
    modified: Dict[str, Any],
    bounds: Dict[str, Tuple[float, float]] = None,
) -> Dict[str, Any]:
    """
    Calculate drift with optional numeric bounds checking.

    Args:
        original: Original SceneGraph
        modified: Modified SceneGraph
        bounds: Dict of {key: (min, max)} bounds to enforce

    Returns:
        Dictionary with drift score and any bound violations
    """
    drift_score = calculate_drift_score(original, modified)
    violations = []

    if bounds:
        numeric_diffs = get_numeric_differences(original, modified)
        for key, (orig, new) in numeric_diffs.items():
            if key in bounds:
                min_val, max_val = bounds[key]
                if new < min_val or new > max_val:
                    violations.append(
                        f"{key} value {new} violates bounds [{min_val}, {max_val}]"
                    )

    return {
        "drift_score": drift_score,
        "bound_violations": violations,
        "is_valid": len(violations) == 0,
    }
