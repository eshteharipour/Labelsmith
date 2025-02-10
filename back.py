import json
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from prod2vec.dataset.isee_cleaner import read_dataset

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
PAGE_SIZE = 1000

# Load dataset
print("Lading dataframe...")
fltr_df, orig_df, state_file, default_image = read_dataset()
print("Finished loading dataframe.")


# Load or initialize state
if os.path.exists(state_file):
    with open(state_file, "r", encoding="utf-8") as f:
        state = json.load(f)
else:
    state = {"selected_images": [], "last_page": 0}
    os.makedirs(os.path.dirname(state_file), exist_ok=True)
    with open(state_file, "w", encoding="utf-8") as f:
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

    page_data = fltr_df.iloc[start_idx:end_idx].reset_index().to_dict("records")
    total_pages = len(fltr_df) // PAGE_SIZE + (1 if len(fltr_df) % PAGE_SIZE > 0 else 0)

    state["last_page"] = page
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

    return {
        "images": page_data,
        "total_pages": total_pages,
        "current_page": page,
        "selected_images": state["selected_images"],
    }


@app.get("/api/images/selected")
async def get_selected_images():
    selected_df = orig_df[
        orig_df["basename"].isin(state["selected_images"])
    ].drop_duplicates("basename")
    return {"images": selected_df.reset_index().to_dict("records")}


@app.post("/api/images/update")
async def update_image(update: ImageUpdate):
    if update.selected and update.basename not in state["selected_images"]:
        state["selected_images"].append(update.basename)
    elif not update.selected and update.basename in state["selected_images"]:
        state["selected_images"].remove(update.basename)

    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

    return {"success": True}


@app.get("/api/images/file/{image_id}")
async def get_image(image_id: int):
    if image_id < 0 or image_id >= len(fltr_df):
        raise HTTPException(status_code=400, detail="Image not found")

    try:
        image_path = fltr_df.loc[image_id, "path"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
