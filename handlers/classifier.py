"""
Classifier Handler for image dataset classification.

Handles image classification, labeling, and status management.
"""

import os
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel
from utils import get_default_image_path, load_json, save_json

# Only import if the module exists
try:
    from prod2vec.dataset.isee_classifier import read_dataset, save_text_dumps

    CLASSIFIER_AVAILABLE = True
except ImportError:
    CLASSIFIER_AVAILABLE = False
    print("Warning: prod2vec.dataset.isee_classifier not available")

router = APIRouter()

# Configuration
PAGE_SIZE = int(os.getenv("CLASSIFIER_PAGE_SIZE", "100"))
SAVE_LAST_PAGE_ON_PAGE_CHANGE = (
    os.getenv("SAVE_LAST_PAGE_ON_PAGE_CHANGE", "false").lower() == "true"
)

# Global state
_fltr_df = None
_clf_dict = None
_orig_dict = None
_state_file = None
_state: Dict[str, Any] = {"settings": {}, "selected_images": {}}
_default_image = None
_statuses: List[str] = []
_cluster_col = None
_groups_idx2cluster = None
_clusters = None
_prev_groups_cluster_col = None


def init_classifier():
    """Initialize the classifier by loading datasets."""
    global _fltr_df, _clf_dict, _orig_dict, _state_file, _state, _default_image, _statuses, _cluster_col

    if not CLASSIFIER_AVAILABLE:
        print("Classifier module not available - using dummy data")
        _state = {"settings": {}, "selected_images": {}}
        _default_image = get_default_image_path()
        _statuses = []
        return

    print("Loading classifier dataset...")
    (
        _fltr_df,
        _clf_dict,
        _orig_dict,
        _state_file,
        _state,
        _default_image,
        _statuses,
        _cluster_col,
    ) = read_dataset()
    print(f"Loaded {len(_fltr_df)} images for classification")


# Initialize on module load if this router is used
if CLASSIFIER_AVAILABLE:
    init_classifier()


class ImageUpdate(BaseModel):
    """Model for image classification updates."""

    path: str
    status: str


class MainResponse(BaseModel):
    """Main response model for paginated data."""

    images: List[Dict[str, Any]]
    total_pages: int
    current_page: int
    selected_images: Dict[str, str]
    statuses: List[str]


@router.get("/load_settings")
async def load_settings():
    """Load user settings from state."""
    return {"settings": _state.get("settings", {})}


@router.post("/save_settings")
async def save_settings(request: Request):
    """Save user settings to state."""
    data = await request.json()
    _state["settings"] = data
    if _state_file:
        save_json(_state_file, _state)
    return {"success": True}


@router.post("/sync_classifications")
async def sync_classifications():
    """Sync classifications to disk."""
    if not CLASSIFIER_AVAILABLE or not _state_file:
        return {"success": False, "error": "Classifier not available"}

    save_json(_state_file, _state)
    save_text_dumps(_state)
    return {"success": True}


@router.get("/images")
async def get_images(page: int = 0):
    """Get paginated images."""
    if not CLASSIFIER_AVAILABLE or _fltr_df is None:
        return MainResponse(
            images=[], total_pages=0, current_page=0, selected_images={}, statuses=[]
        )

    start_idx = page * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE

    page_data = _fltr_df.iloc[start_idx:end_idx].reset_index().to_dict("records")
    total_pages = (len(_fltr_df) + PAGE_SIZE - 1) // PAGE_SIZE

    if SAVE_LAST_PAGE_ON_PAGE_CHANGE and _state_file:
        _state["settings"]["lastPage"] = page
        save_json(_state_file, _state)

    return MainResponse(
        images=page_data,
        total_pages=total_pages,
        current_page=page,
        selected_images=_state.get("selected_images", {}),
        statuses=_statuses,
    )


@router.get("/groups")
async def get_groups(page: int = 0):
    """Get images grouped by cluster."""
    global _prev_groups_cluster_col, _clusters, _groups_idx2cluster

    if not CLASSIFIER_AVAILABLE or _fltr_df is None:
        return MainResponse(
            images=[], total_pages=0, current_page=0, selected_images={}, statuses=[]
        )

    if _cluster_col != _prev_groups_cluster_col:
        _prev_groups_cluster_col = _cluster_col
        _clusters = list(_fltr_df[_cluster_col].unique())
        _groups_idx2cluster = dict(zip(range(len(_clusters)), _clusters))

    if page >= len(_clusters):
        return MainResponse(
            images=[],
            total_pages=len(_clusters) if _clusters else 0,
            current_page=page,
            selected_images={},
            statuses=[],
        )

    page_data = (
        _fltr_df[_fltr_df[_cluster_col] == _groups_idx2cluster[page]]
        .reset_index()
        .to_dict("records")
    )
    total_pages = len(_clusters)

    if SAVE_LAST_PAGE_ON_PAGE_CHANGE and _state_file:
        _state["settings"]["lastPage"] = page
        save_json(_state_file, _state)

    return MainResponse(
        images=page_data,
        total_pages=total_pages,
        current_page=page,
        selected_images=_state.get("selected_images", {}),
        statuses=_statuses,
    )


@router.get("/images/selected")
async def get_selected_images():
    """Get all selected/classified images."""
    if not CLASSIFIER_AVAILABLE:
        return {"images": [], "selected_images": {}}

    images = [
        (
            _clf_dict.get(k)
            or _orig_dict.get(k)
            or {"id": i, "path": k, "basename": os.path.basename(k)}
        )
        for i, k in enumerate(_state.get("selected_images", {}).keys())
    ]

    return {
        "images": images,
        "selected_images": _state.get("selected_images", {}),
    }


@router.post("/images/update")
async def update_image(update: ImageUpdate):
    """Update image classification status."""
    if update.status and update.path:
        _state.setdefault("selected_images", {})[update.path] = update.status
    elif not update.status and update.path in _state.get("selected_images", {}):
        _state["selected_images"].pop(update.path)

    if _state_file:
        save_json(_state_file, _state)

    return {"success": True}


@router.get("/images/file")
async def get_image_file(image_path: str):
    """Serve an image file."""
    if not image_path:
        return FileResponse(_default_image or get_default_image_path())

    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail=f"Image not found: {image_path}")

    try:
        return FileResponse(image_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
