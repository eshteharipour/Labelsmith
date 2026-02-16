"""
Cluster Handler for clustered image viewing.

Displays images grouped by cluster ID with support for both local and server images.
"""

import os
from typing import Any, Dict, List

import httpx
import pandas as pd
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import FileResponse

from dataset import cluster
from dataset.settings import LCSCIseeCLip, LIPDataset, get_default_image

router = APIRouter()

# Configuration
PAGE_SIZE = int(os.getenv("CLUSTER_PAGE_SIZE", "100"))
SAVE_LAST_PAGE_ON_PAGE_CHANGE = (
    os.getenv("SAVE_LAST_PAGE_ON_PAGE_CHANGE", "false").lower() == "true"
)

# Global state
_df = None
_state: Dict[str, Any] = {"settings": {}}
_state_file = None
_default_image = None
_cluster_col = None


def init_cluster():
    """Initialize the cluster viewer by loading datasets."""
    global _df, _state, _state_file, _default_image, _cluster_col

    print("Loading cluster dataset...")
    _df, _state_file, _state, _default_image, _cluster_col = cluster.read_dataset()
    print(f"Loaded {len(_df)} images in clusters")


# Initialize on module load
init_cluster()


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


@router.get("/images")
async def get_images(page: int = 0):
    """Get paginated clustered images."""
    from dataset.core import save_json

    start_idx = page * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE

    page_data = _df.iloc[start_idx:end_idx].reset_index().to_dict("records")
    total_pages = (len(_df) + PAGE_SIZE - 1) // PAGE_SIZE

    # Clean up cluster_id field
    for item in page_data:
        if (
            "cluster_id" not in item
            or pd.isna(item["cluster_id"])
            or int(item["cluster_id"]) < 0
        ):
            item["cluster_id"] = None

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
    """Serve a local image file."""
    if not image_path:
        return FileResponse(_default_image)

    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail=f"Image not found: {image_path}")

    try:
        return FileResponse(image_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/proxy-image")
async def proxy_image(url: str):
    """
    Proxy external images through the backend.

    This allows the frontend to display images from external URLs
    while avoiding CORS issues.
    """
    if not url:
        return FileResponse(_default_image)

    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(url, timeout=10.0)

            return Response(
                content=response.content,
                media_type=response.headers.get("content-type", "image/jpeg"),
                headers={
                    "Cache-Control": "public, max-age=86400"  # Cache for 24 hours
                },
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch image: {str(e)}")
