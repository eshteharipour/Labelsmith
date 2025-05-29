import os

import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from prod2vec.dataset.isee_matcher import (
    DatasetEnum,
    read_dataset,
    save_dataset,
    save_json,
)

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
COLUMNS = ["source_name", "source_image", "target_name", "target_image", "matching"]


# Load dataset
print("Lading dataframe...")
DATASET = DatasetEnum(os.environ["dataset"].lower().strip())
SHOW_REVIEWD = os.environ["show_reviewed"].lower().strip() == "true"
df, state, state_file, default_image = read_dataset(
    DATASET, SHOW_REVIEWD, os.environ["show_matchings"], os.environ["must_have_farsi"]
)
result_df = pd.DataFrame(columns=COLUMNS, dtype=object)
print("Finished loading dataframe.")


class MatchUpdate(BaseModel):
    id: str
    source_name: str
    source_image: str
    target_name: str
    target_image: str
    matching: bool


@app.get("/api/load_settings")
async def load_page():
    return {"settings": state["settings"]}


@app.post("/api/save_settings")
async def save_page(request: Request):
    data = await request.json()
    state["settings"] = data
    save_json(state_file, state)

    return {"success": True}


@app.post("/api/sync_changes")
async def save_data():

    save_dataset(result_df)
    return {"success": True}


@app.post("/api/sync_page")
async def save_data_page(request: Request):
    page = await request.json()
    page = int(page["page"])
    start_idx = page * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE

    page_data = df.iloc[start_idx:end_idx].reset_index()

    save_dataset(page_data)
    return {"success": True}


@app.post("/api/sync_all")
async def save_data_all():

    save_dataset(df)
    return {"success": True}


@app.get("/api/images")
async def get_images(page: int = 0):
    start_idx = page * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE

    page_data = df.iloc[start_idx:end_idx].reset_index().to_dict("records")
    total_pages = len(df) // PAGE_SIZE + (1 if len(df) % PAGE_SIZE > 0 else 0)

    # Save last_page on changing page
    if SAVE_LAST_PAGE_ON_PAGE_CHANGE:
        state["settings"]["lastPage"] = page
        save_json(state_file, state)

    return {
        "images": page_data,
        "total_pages": total_pages,
        "current_page": page,
    }


@app.post("/api/images/update")
async def update_image(update: MatchUpdate):
    global result_df
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
    result_df = pd.concat([result_df, data], ignore_index=True)

    q = df.loc[update.id]
    if update.source_name != q.source_name:
        return {"success": False}
    if update.source_image != q.source_image:
        return {"success": False}
    if update.target_name != q.target_name:
        return {"success": False}
    if update.target_image != q.target_image:
        return {"success": False}

    df.loc[update.id, "matching"] = update.matching

    return {"success": True}


@app.get("/api/images/file")
async def get_image(image_path: str):
    if not image_path:
        return FileResponse(default_image)

    if not os.path.exists(image_path):
        raise HTTPException(
            status_code=404, detail=f"Image file not found {image_path}"
        )

    try:
        return FileResponse(image_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Mount static files for frontend
app.mount("/", StaticFiles(directory="cleaner/dist", html=True), name="static")
