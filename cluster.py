import os

import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from prod2vec.dataset.isee_cluster import read_dataset, save_json

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


# Load dataset
print("Lading dataframe...")
df, state_file, state, default_image, cluster_col = read_dataset()
print("Finished loading dataframe.")


@app.get("/api/load_settings")
async def load_page():
    return {"settings": state["settings"]}


@app.post("/api/save_settings")
async def save_page(request: Request):
    data = await request.json()
    state["settings"] = data
    save_json(state_file, state)

    return {"success": True}


@app.get("/api/images")
async def get_images(page: int = 0):
    start_idx = page * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE

    page_data = df.iloc[start_idx:end_idx].reset_index().to_dict("records")
    total_pages = len(df) // PAGE_SIZE + (1 if len(df) % PAGE_SIZE > 0 else 0)

    for item in page_data:
        if (
            "cluster_id" not in item
            or pd.isna(item["cluster_id"])
            or int(item["cluster_id"]) < 0
        ):
            item["cluster_id"] = None

    if SAVE_LAST_PAGE_ON_PAGE_CHANGE:
        state["settings"]["last_page"] = page
        save_json(state_file, state)

    return {
        "images": page_data,
        "total_pages": total_pages,
        "current_page": page,
    }


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
