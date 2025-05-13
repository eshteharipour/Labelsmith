import json
import os

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from schema_core import CrawlerProducts, ReferenceProducts, Site
from sqlalchemy import create_engine, update
from sqlalchemy.orm import Session, aliased, sessionmaker
from sqlalchemy.sql import func

load_dotenv()
app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Constants
PAGE_SIZE = 100
SAVE_LAST_PAGE_ON_PAGE_CHANGE = False
SHOW_REVIEWD = os.environ["show_reviewed"].lower().strip() == "true"
STATE_FILE = "state.json"
DEFAULT_IMAGE = "https://isee.sisoog.com/assets/img/noimage.png"
ICDN_URL = "https://icdn.sisoog.com/"


def save_json(path: str, d: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)


def create_session(dbname: str, autocommit=False):
    """
    Creates a database session.

    Returns:
        Session: The database session.
    """
    if dbname == "isee":
        db_url = os.environ["DB_URL_ISEE"]
    elif dbname == "core":
        db_url = os.environ["DB_URL_CORE"]

    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=autocommit, autoflush=False, bind=engine)
    db = SessionLocal()
    return db


def get_all_crawler_products(db: Session, show_reviewed=False, only_enabled=True):
    """
    Retrieves rows from the CrawlerProducts table, and optionally only enabled sites.

    Args:
        db (Session): The database session.
        cp_ids (list[int], optional): List of CrawlerProducts IDs to filter by. Defaults to [].

    Returns:
        List[CrawlerProducts]: A list of CrawlerProducts objects, either all or filtered by cp_ids.
    """
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

    if show_reviewed == False:
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


class CPUpdate(BaseModel):
    id: int
    ref_pid: int


# Load dataset
print("Lading dataframe...")
session = create_session("core")
data = get_all_crawler_products(session)
state = {"settings": {}}
print("Finished loading database.")


@app.get("/api/load_settings")
async def load_page():
    return {"settings": state["settings"]}


@app.post("/api/save_settings")
async def save_page(request: Request):
    data = await request.json()
    state["settings"] = data
    save_json(STATE_FILE, state)

    return {"success": True}


@app.get("/api/images")
async def get_images(page: int = 0):
    start_idx = page * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE

    page_data = data[start_idx:end_idx]
    total_pages = len(data) // PAGE_SIZE + (1 if len(data) % PAGE_SIZE > 0 else 0)

    # Save last_page on changing page
    if SAVE_LAST_PAGE_ON_PAGE_CHANGE:
        state["settings"]["lastPage"] = page
        save_json(STATE_FILE, state)

    return {
        "images": page_data,
        "total_pages": total_pages,
        "current_page": page,
    }


@app.post("/api/images/update")
async def update_image(update: CPUpdate):
    result = update_groups_single(session, update.id, update.ref_pid)
    if result == True:
        return {"success": True}
    else:
        return {"success": False}


@app.get("/api/proxy-image")
async def proxy_image(url: str):
    if not url:
        return FileResponse(DEFAULT_IMAGE)

    try:
        # Use httpx for making the HTTP request
        async with httpx.AsyncClient(follow_redirects=True) as client:
            # Set a reasonable timeout
            response = await client.get(url, timeout=10.0)

            # Return the image with the same content type
            return Response(
                content=response.content,
                media_type=response.headers.get("content-type", "image/jpeg"),
                headers={
                    "Cache-Control": "public, max-age=86400"  # Cache for 24 hours
                },
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch image: {str(e)}")


# Mount static files for frontend
app.mount("/", StaticFiles(directory="cleaner/dist", html=True), name="static")
