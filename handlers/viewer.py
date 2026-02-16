"""
Viewer Handler for image similarity viewing.

Displays images with their nearest neighbors based on different similarity metrics.
"""

import os
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse

from dataset import viewer
from dataset.settings import LCSCIseeCLip, LIPDataset, get_default_image, save_csv

router = APIRouter()

# Configuration
PAGE_SIZE = int(os.getenv("VIEWER_PAGE_SIZE", "100"))
SAVE_LAST_PAGE_ON_PAGE_CHANGE = (
    os.getenv("SAVE_LAST_PAGE_ON_PAGE_CHANGE", "false").lower() == "true"
)

# Global state
_df = None
_state: Dict[str, Any] = {"settings": {}}
_state_file = None
_default_image = None


def init_viewer():
    """Initialize the viewer by loading datasets."""
    global _df, _state, _state_file, _default_image

    print("Loading viewer dataset...")
    _df, _state, _state_file, _default_image = viewer.read_dataset()
    print(f"Loaded {len(_df)} images for viewing")


# Initialize on module load
init_viewer()


@router.get("/load_settings")
async def load_settings():
    """Load user settings from state."""
    return {"settings": _state.get("settings", {})}


@router.post("/save_settings")
async def save_settings(request: Request):
    """Save user settings to state."""
    from dataset.core import save_json

    data = await request.json()
    _state["settings"] = data
    save_json(_state_file, _state)
    return {"success": True}


@router.post("/sync_page")
async def sync_page(request: Request):
    """Save current page to file."""
    data = await request.json()
    page = int(data["page"])
    start_idx = page * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE

    page_data = _df.iloc[start_idx:end_idx].reset_index()

    try:
        viewer.save_dataset(page_data)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/images")
async def get_images(page: int = 0):
    """Get paginated images with similarity data."""
    from dataset.core import save_json

    start_idx = page * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE

    page_data = _df.iloc[start_idx:end_idx].reset_index().to_dict("records")
    total_pages = (len(_df) + PAGE_SIZE - 1) // PAGE_SIZE

    if SAVE_LAST_PAGE_ON_PAGE_CHANGE:
        _state["settings"]["lastPage"] = page
        save_json(_state_file, _state)

    return {
        "images": page_data,
        "total_pages": total_pages,
        "current_page": page,
    }


@router.get("/images/file")
async def get_image_file(image_path: str):
    """Serve an image file."""
    if not image_path:
        return FileResponse(_default_image)

    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail=f"Image not found: {image_path}")

    try:
        return FileResponse(image_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
