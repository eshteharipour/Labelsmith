"""
Shop Handler for product reference matching.

Handles crawler products and their reference product recommendations.
"""

import os
from typing import Any, Dict, List

import httpx
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import FileResponse
from prod2vec.dataset.schemas.schema_core import (
    CrawlerProducts,
    ReferenceProducts,
    Site,
)
from pydantic import BaseModel
from sqlalchemy import create_engine, update
from sqlalchemy.orm import Session, aliased, sessionmaker
from sqlalchemy.sql import func

from utils import get_default_image_path, load_json, save_json

load_dotenv()


router = APIRouter()

# Configuration
PAGE_SIZE = int(os.getenv("SHOP_PAGE_SIZE", "100"))
SAVE_LAST_PAGE_ON_PAGE_CHANGE = (
    os.getenv("SAVE_LAST_PAGE_ON_PAGE_CHANGE", "false").lower() == "true"
)
SHOW_REVIEWED = os.getenv("show_reviewed", "false").lower().strip() == "true"
STATE_FILE = "state_shop.json"
DEFAULT_IMAGE = "https://isee.sisoog.com/assets/img/noimage.png"
ICDN_URL = "https://icdn.sisoog.com/"

# Global state
_session = None
_data: List[Any] = []
_state: Dict[str, Any] = {"settings": {}}


def create_session(dbname: str, autocommit=False):
    """Create a database session."""
    if dbname == "isee":
        db_url = os.environ.get("DB_URL_ISEE")
    elif dbname == "core":
        db_url = os.environ.get("DB_URL_CORE")
    else:
        return None

    if not db_url:
        return None

    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=autocommit, autoflush=False, bind=engine)
    return SessionLocal()


def get_all_crawler_products(db: Session, show_reviewed=False, only_enabled=True):
    """Retrieve crawler products with reference product recommendations."""
    ReferenceProducts2 = aliased(ReferenceProducts, name="ref_products2")

    query = db.query(
        CrawlerProducts.id,
        CrawlerProducts.name.label("cp_name"),
        func.concat(ICDN_URL, CrawlerProducts.picture).label("cp_image"),
        CrawlerProducts.ref_pid,
        ReferenceProducts2.name.label("ref_name"),
        func.concat(ICDN_URL, ReferenceProducts2.image).label("ref_image"),
        CrawlerProducts.recommended_ref_pid,
        ReferenceProducts.name.label("recom_ref_name"),
        func.concat(ICDN_URL, ReferenceProducts.image).label("recom_ref_image"),
    )

    query = query.filter(CrawlerProducts.recommended_ref_pid.isnot(None))

    if not show_reviewed:
        query = query.filter(
            CrawlerProducts.recommended_ref_pid.is_distinct_from(
                CrawlerProducts.ref_pid
            )
        )

    if only_enabled:
        query = query.join(Site).filter(Site.disabled == False)

    query = query.join(
        ReferenceProducts, ReferenceProducts.id == CrawlerProducts.recommended_ref_pid
    ).join(ReferenceProducts2, ReferenceProducts2.id == CrawlerProducts.ref_pid)

    return query.all()


def update_groups_single(db: Session, id_: int, ref_pid: int) -> bool:
    """Update a single crawler product's reference PID."""
    try:
        stmt = (
            update(CrawlerProducts)
            .where(CrawlerProducts.id == id_)
            .values(ref_pid=ref_pid)
        )
        result = db.execute(stmt)
        db.commit()

        if result.rowcount > 0:
            print(f"Product updated with id {id_}")
            return True
        else:
            print(f"No product found with id {id_}")
            return False
    except Exception as e:
        print(f"Error updating product with id {id_}: {e}")
        db.rollback()
        return False


def init_shop():
    """Initialize the shop handler by loading data."""
    global _session, _data, _state

    print("Loading shop database...")
    _session = create_session("core")
    if _session:
        _data = get_all_crawler_products(_session, SHOW_REVIEWED)
        print(f"Loaded {len(_data)} products")
    _state = load_json(STATE_FILE, {"settings": {}})


# Initialize on module load if this router is used
init_shop()


class CPUpdate(BaseModel):
    """Model for crawler product updates."""

    id: int
    ref_pid: int


@router.get("/load_settings")
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


@router.get("/images")
async def get_images(page: int = 0):
    """Get paginated product matching pairs."""
    start_idx = page * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE

    page_data = _data[start_idx:end_idx]
    total_pages = (len(_data) + PAGE_SIZE - 1) // PAGE_SIZE

    if SAVE_LAST_PAGE_ON_PAGE_CHANGE:
        _state["settings"]["lastPage"] = page
        save_json(STATE_FILE, _state)

    return {
        "images": page_data,
        "total_pages": total_pages,
        "current_page": page,
    }


@router.post("/images/update")
async def update_product(update: CPUpdate):
    """Update a crawler product's reference PID."""
    if not _session:
        return {"success": False, "error": "Shop not available"}

    result = update_groups_single(_session, update.id, update.ref_pid)
    return {"success": result}


@router.get("/proxy-image")
async def proxy_image(url: str):
    """Proxy external images through the backend."""
    if not url:
        return FileResponse(DEFAULT_IMAGE)

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
