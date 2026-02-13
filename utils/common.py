"""
Utility functions shared across handlers.
"""

import json
import os
from typing import Any, Dict


def save_json(path: str, data: Dict[str, Any]) -> None:
    """
    Save a dictionary as JSON to a file.

    Args:
        path: File path to save to
        data: Dictionary to save
    """
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_json(path: str, default: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Load JSON from a file with fallback to default.

    Args:
        path: File path to load from
        default: Default value if file doesn't exist

    Returns:
        Loaded dictionary or default
    """
    if default is None:
        default = {}

    if not os.path.exists(path):
        return default

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return default


def get_default_image_path() -> str:
    """
    Get the path to the default placeholder image.

    Returns:
        Path to default image or URL
    """
    default_url = "https://isee.sisoog.com/assets/img/noimage.png"
    default_local = "assets/noimage.png"

    if os.path.exists(default_local):
        return default_local
    return default_url


def ensure_dir(path: str) -> None:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path
    """
    os.makedirs(path, exist_ok=True)
