import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from prod2vec.dataset.isee_cleaner import read_dataset, save_json, save_text_dumps

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
groups_idx2cluster = None
clusters = None
prev_groups_cluster_col = None


# Load dataset
print("Lading dataframe...")
fltr_df, state_file, state, default_image, statuses, cluster_col = read_dataset()
print("Finished loading dataframe.")


class ImageUpdate(BaseModel):
    path: str
    status: str


class ClusterUpdate(BaseModel):
    name: str
    cluster_id: str


class MainResponse(BaseModel):
    images: list[dict]
    total_pages: int
    current_page: int
    selected_images: dict[str, str]
    statuses: list[str]


@app.get("/api/load_settings")
async def save_page():
    return {"settings": state["settings"]}


@app.post("/api/save_settings")
async def save_page(request: Request):
    data = await request.json()
    state["settings"] = data
    save_json(state_file, state)

    return {"success": True}


@app.post("/api/sync_classifications")
async def sync_flush():
    save_json(state_file, state)
    save_text_dumps(state)

    return {"success": True}


@app.get("/api/images")
async def get_images(page: int = 0):
    start_idx = page * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE

    page_data = fltr_df.iloc[start_idx:end_idx].reset_index().to_dict("records")
    total_pages = len(fltr_df) // PAGE_SIZE + (1 if len(fltr_df) % PAGE_SIZE > 0 else 0)

    # Save last_page on changing page
    if SAVE_LAST_PAGE_ON_PAGE_CHANGE:
        state["settings"]["last_page"] = page
        await save_json(page)

    return MainResponse(
        images=page_data,
        total_pages=total_pages,
        current_page=page,
        selected_images=state["selected_images"],
        statuses=statuses,
    )


@app.get("/api/groups")
async def get_groups(page: int = 0):
    global prev_groups_cluster_col, clusters, groups_idx2cluster
    if cluster_col != prev_groups_cluster_col:
        prev_groups_cluster_col = cluster_col
        clusters = list(fltr_df[cluster_col].unique())  # Has None so do not sort!
        groups_idx2cluster = dict(zip(range(len(clusters)), clusters))

    if page >= len(clusters):
        return {}

    page_data = (
        fltr_df[fltr_df[cluster_col] == groups_idx2cluster[page]]
        .reset_index()
        .to_dict("records")
    )
    clusters = fltr_df[cluster_col].unique()
    total_pages = len(clusters)

    # Save last_page on changing page
    if SAVE_LAST_PAGE_ON_PAGE_CHANGE:
        state["settings"]["last_page"] = page
        await save_json(page)

    return MainResponse(
        images=page_data,
        total_pages=total_pages,
        current_page=page,
        selected_images=state["selected_images"],
        statuses=statuses,
    )


@app.get("/api/images/selected")
async def get_selected_images():
    images = [
        {"id": i, "path": k, "basename": os.path.basename(k)}
        for i, k in enumerate(state["selected_images"].keys())
    ]
    return {
        "images": images,
        "selected_images": state["selected_images"],
    }


@app.post("/api/images/update")
async def update_image(update: ImageUpdate):
    if update.status and update.path:
        state["selected_images"].update({update.path: update.status})
    elif not update.status and update.path in state["selected_images"]:
        state["selected_images"].pop(update.path)

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


@app.get("/api/images/selected_file")
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
