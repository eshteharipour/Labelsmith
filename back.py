import json
import os

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from dataset.settings import LCSCIseeCLip

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants
DATA_FILE = LCSCIseeCLip.dataset_path
STATE_FILE = "artifacts/state.json"
PAGE_SIZE = 100

# Load dataset
if not os.path.exists(DATA_FILE):
    raise FileNotFoundError(f"Dataset file '{DATA_FILE}' not found.")

df = pd.read_csv(DATA_FILE, sep="\t", dtype=object, keep_default_na=False)
df.index.name = "id"

# Load or initialize state
if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        state = json.load(f)
else:
    state = {"selected_images": [], "last_page": 0}
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


class ImageUpdate(BaseModel):
    basename: str
    selected: bool


@app.get("/api/last")
async def get_last():
    return {"last_page": state["last_page"]}


@app.get("/api/images")
async def get_images(page: int = 0):
    start_idx = page * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE

    page_data = df.iloc[start_idx:end_idx].reset_index().to_dict("records")
    total_pages = len(df) // PAGE_SIZE + (1 if len(df) % PAGE_SIZE > 0 else 0)

    state["last_page"] = page
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

    return {
        "images": page_data,
        "total_pages": total_pages,
        "current_page": page,
        "selected_images": state["selected_images"],
    }


@app.get("/api/images/selected")
async def get_selected_images():
    selected_df = df[df["basename"].isin(state["selected_images"])]
    return {"images": selected_df.reset_index().to_dict("records")}


@app.post("/api/images/update")
async def update_image(update: ImageUpdate):
    if update.selected and update.basename not in state["selected_images"]:
        state["selected_images"].append(update.basename)
    elif not update.selected and update.basename in state["selected_images"]:
        state["selected_images"].remove(update.basename)

    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

    return {"success": True}


@app.get("/api/images/file/{image_id}")
async def get_image(image_id: int):
    try:
        if image_id < 0 or image_id >= len(df):
            raise HTTPException(status_code=404, detail="Image not found")

        image_path = df.loc[image_id, "path"]
        if not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail="Image file not found")

        return FileResponse(image_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Mount static files for frontend
app.mount("/", StaticFiles(directory="cleaner/dist", html=True), name="static")
