"""
Text Labeler Handler for JSONL datasets.

This module handles text labeling for image datasets stored in JSONL format.
Each line in the JSONL file contains: {"image": "path/to/image.jpg", "text": "label"}
"""

import json
import os
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel
from utils import get_default_image_path, load_json, save_json

router = APIRouter()

# Configuration
PAGE_SIZE = int(os.getenv("LABELER_PAGE_SIZE", "100"))
SAVE_LAST_PAGE_ON_PAGE_CHANGE = (
    os.getenv("SAVE_LAST_PAGE_ON_PAGE_CHANGE", "false").lower() == "true"
)
STATE_FILE = os.getenv("LABELER_STATE_FILE", "state_labeler.json")
JSONL_FILE = os.getenv("LABELER_JSONL_FILE", "dataset.jsonl")
IMAGE_BASE_PATH = os.getenv("LABELER_IMAGE_BASE_PATH", "")

# Global state
_state: Dict[str, Any] = {"settings": {}}
_dataset: List[Dict[str, str]] = []
_default_image = get_default_image_path()


def load_jsonl(file_path: str) -> List[Dict[str, str]]:
    """
    Load JSONL file into a list of dictionaries.

    Args:
        file_path: Path to JSONL file

    Returns:
        List of dictionaries, each with 'image' and 'text' keys
    """
    if not os.path.exists(file_path):
        return []

    data = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                # Ensure required fields exist
                if "image" not in obj:
                    obj["image"] = f"missing_image_{line_num}.jpg"
                if "text" not in obj:
                    obj["text"] = ""
                data.append(obj)
            except json.JSONDecodeError as e:
                print(f"Warning: Skipping invalid JSON on line {line_num}: {e}")
                continue

    return data


def save_jsonl(file_path: str, data: List[Dict[str, str]]) -> None:
    """
    Save list of dictionaries to JSONL file.

    Args:
        file_path: Path to JSONL file
        data: List of dictionaries to save
    """
    # Create backup
    if os.path.exists(file_path):
        backup_path = file_path + ".backup"
        try:
            with open(file_path, "r") as src, open(backup_path, "w") as dst:
                dst.write(src.read())
        except Exception as e:
            print(f"Warning: Could not create backup: {e}")

    # Write new data
    with open(file_path, "w", encoding="utf-8") as f:
        for item in data:
            json.dump(item, f, ensure_ascii=False)
            f.write("\n")


def update_item_in_dataset(image_path: str, text: str) -> bool:
    """
    Update a single item in the dataset by image path.

    Args:
        image_path: Path to the image
        text: New text label

    Returns:
        True if item was found and updated, False otherwise
    """
    global _dataset

    for item in _dataset:
        if item.get("image") == image_path:
            item["text"] = text
            return True

    return False


def init_text_labeler():
    """Initialize the text labeler by loading data."""
    global _state, _dataset, _default_image

    print(f"Loading text labeler state from: {STATE_FILE}")
    _state = load_json(STATE_FILE, {"settings": {}})

    print(f"Loading JSONL dataset from: {JSONL_FILE}")
    _dataset = load_jsonl(JSONL_FILE)
    print(f"Loaded {len(_dataset)} items from JSONL")

    _default_image = get_default_image_path()


# Initialize on module load
init_text_labeler()


class TextUpdate(BaseModel):
    """Model for text label updates."""

    path: str
    text: str


class MainResponse(BaseModel):
    """Main response model for paginated data."""

    images: List[Dict[str, Any]]
    total_pages: int
    current_page: int


@router.get("/load_settings", response_model=Dict[str, Any])
async def load_settings():
    """Load user settings from state."""
    return {"settings": _state.get("settings", {})}


@router.post("/save_settings")
async def save_settings(request: Request):
    """Save user settings to state."""
    data = await request.json()
    _state["settings"] = data
    save_json(STATE_FILE, _state)
    return {"success": True}


@router.get("/images", response_model=MainResponse)
async def get_images(page: int = 0):
    """
    Get paginated images from the JSONL dataset.

    Args:
        page: Page number (0-indexed)

    Returns:
        Paginated image data with metadata
    """
    start_idx = page * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE

    page_data = _dataset[start_idx:end_idx]
    total_pages = (len(_dataset) + PAGE_SIZE - 1) // PAGE_SIZE

    # Save last page if configured
    if SAVE_LAST_PAGE_ON_PAGE_CHANGE:
        _state["settings"]["lastPage"] = page
        save_json(STATE_FILE, _state)

    return MainResponse(
        images=page_data,
        total_pages=total_pages,
        current_page=page,
    )


@router.post("/images/update")
async def update_image_text(update: TextUpdate):
    """
    Update the text label for a specific image.

    Args:
        update: Update request with image path and new text

    Returns:
        Success status
    """
    success = update_item_in_dataset(update.path, update.text)

    if not success:
        raise HTTPException(
            status_code=404, detail=f"Image not found in dataset: {update.path}"
        )

    # Auto-save the change to the JSONL file
    try:
        save_jsonl(JSONL_FILE, _dataset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save changes: {str(e)}")

    return {"success": True}


@router.post("/sync_page")
async def sync_page(request: Request):
    """
    Save all items on the current page to the JSONL file.

    This is useful for batch saving after multiple edits.
    """
    try:
        save_jsonl(JSONL_FILE, _dataset)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save page: {str(e)}")


@router.get("/images/file")
async def get_image_file(image_path: str):
    """
    Serve an image file from the filesystem.

    Args:
        image_path: Relative or absolute path to the image

    Returns:
        Image file response
    """
    if not image_path:
        return FileResponse(_default_image)

    # Construct full path if base path is configured
    if IMAGE_BASE_PATH:
        full_path = os.path.join(IMAGE_BASE_PATH, image_path)
    else:
        full_path = image_path

    # Security: Prevent directory traversal
    if ".." in full_path or full_path.startswith("/"):
        if not os.path.isabs(full_path):
            raise HTTPException(status_code=400, detail="Invalid image path")

    if not os.path.exists(full_path):
        # Try without base path
        if os.path.exists(image_path):
            full_path = image_path
        else:
            raise HTTPException(
                status_code=404, detail=f"Image file not found: {image_path}"
            )

    try:
        return FileResponse(full_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error serving image: {str(e)}")


@router.post("/reload")
async def reload_dataset():
    """
    Reload the JSONL dataset from disk.

    Useful if the dataset is modified externally.
    """
    try:
        init_text_labeler()
        return {"success": True, "items_loaded": len(_dataset)}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to reload dataset: {str(e)}"
        )


@router.get("/stats")
async def get_stats():
    """
    Get statistics about the dataset.

    Returns:
        Dataset statistics including total items and labeled/unlabeled counts
    """
    total = len(_dataset)
    labeled = sum(1 for item in _dataset if item.get("text", "").strip())
    unlabeled = total - labeled

    return {
        "total_items": total,
        "labeled": labeled,
        "unlabeled": unlabeled,
        "labeled_percentage": round(labeled / total * 100, 2) if total > 0 else 0,
    }
