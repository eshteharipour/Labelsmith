"""
Matcher Handler for product matching interface.

Handles source-target product matching and evaluation.
"""

import os
from typing import Any, Dict, List

import pandas as pd
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel
from utils import get_default_image_path, load_json, save_json

load_dotenv()

# Only import if the module exists
try:
    from prod2vec.dataset.isee_matcher import DatasetEnum, read_dataset, save_dataset

    MATCHER_AVAILABLE = True
except ImportError:
    MATCHER_AVAILABLE = False
    print("Warning: prod2vec.dataset.isee_matcher not available")

router = APIRouter()

# Configuration
PAGE_SIZE = int(os.getenv("MATCHER_PAGE_SIZE", "100"))
SAVE_LAST_PAGE_ON_PAGE_CHANGE = (
    os.getenv("SAVE_LAST_PAGE_ON_PAGE_CHANGE", "false").lower() == "true"
)
COLUMNS = ["source_name", "source_image", "target_name", "target_image", "matching"]

# Global state
_df = None
_state: Dict[str, Any] = {"settings": {}}
_state_file = "state_matcher.json"
_default_image = None
_result_df = None


def init_matcher():
    """Initialize the matcher by loading datasets."""
    global _df, _state, _default_image, _result_df

    if not MATCHER_AVAILABLE:
        print("Matcher module not available - using dummy data")
        _df = pd.DataFrame(columns=COLUMNS)
        _state = load_json(_state_file, {"settings": {}})
        _default_image = get_default_image_path()
        _result_df = pd.DataFrame(columns=COLUMNS, dtype=object)
        return

    print("Loading matcher dataset...")
    dataset_name = os.getenv("dataset", "").lower().strip()
    show_reviewed = os.getenv("show_reviewed", "false").lower().strip() == "true"
    show_matchings = os.getenv("show_matchings", "")

    try:
        dataset = DatasetEnum(dataset_name)
        _df, _state, state_file_path, _default_image = read_dataset(
            dataset, show_reviewed, show_matchings
        )
        _state_file = state_file_path
        _result_df = pd.DataFrame(columns=COLUMNS, dtype=object)
        print(f"Loaded {len(_df)} matching pairs")
    except Exception as e:
        print(f"Error loading matcher dataset: {e}")
        _df = pd.DataFrame(columns=COLUMNS)
        _state = load_json(_state_file, {"settings": {}})
        _default_image = get_default_image_path()
        _result_df = pd.DataFrame(columns=COLUMNS, dtype=object)


# Initialize on module load if this router is used
if MATCHER_AVAILABLE:
    init_matcher()


class MatchUpdate(BaseModel):
    """Model for match updates."""

    id: str
    source_name: str
    source_image: str
    target_name: str
    target_image: str
    matching: bool


@router.get("/load_settings")
async def load_settings():
    """Load user settings from state."""
    return {"settings": _state.get("settings", {})}


@router.post("/save_settings")
async def save_settings(request: Request):
    """Save user settings to state."""
    data = await request.json()
    _state["settings"] = data
    save_json(_state_file, _state)
    return {"success": True}


@router.post("/sync_changes")
async def sync_changes():
    """Save accumulated changes to file."""
    if not MATCHER_AVAILABLE or _result_df is None:
        return {"success": False, "error": "Matcher not available"}

    try:
        save_dataset(_result_df)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync_page")
async def sync_page(request: Request):
    """Save current page to file."""
    if not MATCHER_AVAILABLE or _df is None:
        return {"success": False, "error": "Matcher not available"}

    data = await request.json()
    page = int(data["page"])
    start_idx = page * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE

    page_data = _df.iloc[start_idx:end_idx].reset_index()

    try:
        save_dataset(page_data)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync_all")
async def sync_all():
    """Save all data to file."""
    if not MATCHER_AVAILABLE or _df is None:
        return {"success": False, "error": "Matcher not available"}

    try:
        save_dataset(_df)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/images")
async def get_images(page: int = 0):
    """Get paginated matching pairs."""
    if not MATCHER_AVAILABLE or _df is None:
        return {
            "images": [],
            "total_pages": 0,
            "current_page": 0,
        }

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


@router.post("/images/update")
async def update_match(update: MatchUpdate):
    """Update a matching pair."""
    global _result_df

    if not MATCHER_AVAILABLE or _df is None:
        return {"success": False, "error": "Matcher not available"}

    # Add to result dataframe
    data = pd.DataFrame(
        [
            [
                update.source_name,
                update.source_image,
                update.target_name,
                update.target_image,
                update.matching,
            ]
        ],
        columns=COLUMNS,
        dtype=object,
    )
    _result_df = pd.concat([_result_df, data], ignore_index=True)

    # Verify update matches existing data
    try:
        q = _df.loc[update.id]
        if (
            update.source_name != q.source_name
            or update.source_image != q.source_image
            or update.target_name != q.target_name
            or update.target_image != q.target_image
        ):
            return {"success": False, "error": "Data mismatch"}

        _df.loc[update.id, "matching"] = update.matching
        return {"success": True}
    except KeyError:
        return {"success": False, "error": "Invalid ID"}


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
