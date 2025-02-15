import json
import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from prod2vec.dataset.isee_cleaner import read_dataset, save_json, sync_state

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
groups_df = None
groups_idx2cluster = None
prev_groups_cluster_col = None


# Load dataset
print("Lading dataframe...")
fltr_df, orig_df, state_file, state, default_image, statuses = read_dataset()
print("Finished loading dataframe.")


class ImageUpdate(BaseModel):
    basename: str
    status: str


class ClusterUpdate(BaseModel):
    name: str
    cluster_id: str


@app.get("/api/last")
async def get_last():
    return {"last_page": state["last_page"]}


@app.post("/api/save_page")
async def save_page(request: Request):
    data = await request.json()
    state["settings"] = data
    save_json(state_file, state)

    return {"success": True}


@app.post("/api/sync")
async def sync_flush():
    sync_state(orig_df, state)

    return {"success": True}


@app.get("/api/images")
async def get_images(page: int = 0):
    start_idx = page * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE

    page_data = fltr_df.iloc[start_idx:end_idx].reset_index().to_dict("records")
    total_pages = len(fltr_df) // PAGE_SIZE + (1 if len(fltr_df) % PAGE_SIZE > 0 else 0)

    # Save last_page on changing page
    if SAVE_LAST_PAGE_ON_PAGE_CHANGE:
        state["last_page"] = page
        await save_json(page)

    return {
        "images": page_data,
        "total_pages": total_pages,
        "current_page": page,
        "selected_images": state["selected_images"],
        "statuses": statuses,
        "settings": state["settings"],
    }


def init_groups(cluster_col):
    print("Initializing df for grouping...")
    return fltr_df.sort_values(cluster_col)


@app.get("/api/groups")
async def get_groups(cluster_col: str, page: int = 0):
    global groups_df, prev_groups_cluster_col, groups_idx2cluster
    if groups_df is None or cluster_col != prev_groups_cluster_col:
        groups_df = init_groups(cluster_col)
        prev_groups_cluster_col = cluster_col
        clusters = list(groups_df[cluster_col].unique())  # None values so do not sort!
        groups_idx2cluster = dict(zip(range(len(clusters)), clusters))

    page_data = (
        groups_df[groups_df[cluster_col] == groups_idx2cluster[page]]
        .reset_index()
        .to_dict("records")
    )
    clusters = groups_df[cluster_col].unique()
    total_pages = len(clusters)

    # Save last_page on changing page
    if SAVE_LAST_PAGE_ON_PAGE_CHANGE:
        state["last_page"] = page
        await save_json(page)

    return {
        "images": page_data,
        "total_pages": total_pages,
        "current_page": page,
        "fixed_groups": state["fixed_groups"],
        "settings": state["settings"],
    }


@app.get("/api/images/selected")
async def get_selected_images():
    selected_df = orig_df[
        orig_df["basename"].isin(state["selected_images"])
    ].drop_duplicates("basename")
    return {"images": selected_df.reset_index().to_dict("records")}


@app.post("/api/images/update")
async def update_image(update: ImageUpdate):
    if update.status and update.basename:
        state["selected_images"].update({update.basename: update.status})
    elif not update.status and update.basename in state["selected_images"]:
        state["selected_images"].pop(update.basename)

    save_json(state_file, state)

    return {"success": True}


@app.post("/api/images/update_cluster")
async def update_image(update: ClusterUpdate):
    if update.name and isinstance(update.cluster_id, int):
        state["fixed_groups"].update({update.name: update.cluster_id})
    elif (
        update.name
        and not isinstance(update.cluster_id, int)
        and update.cluster_id in state["fixed_groups"]
    ):
        state["fixed_groups"].pop(update.name)

    save_json(state_file, state)

    return {"success": True}


@app.get("/api/images/file/{image_id}")
async def get_image(image_id: str):
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
