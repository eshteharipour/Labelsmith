"""
Unified backend for Image Dataset Management System.

This application handles multiple views:
- Classifier: Image classification and labeling
- Matcher: Product matching interface
- Viewer: Image viewer with similarity comparisons
- Cluster: Clustered image viewing
- Shop: Product reference matching
- TextLabeler: JSONL text labeling interface
"""

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from handlers import (
    classifier_router,
    cluster_router,
    matcher_router,
    shop_router,
    text_labeler_router,
    viewer_router,
)

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the FastAPI application."""
    # Startup
    print("Starting Image Dataset Management System...")
    print("Available endpoints:")
    print("  - /classifier")
    print("  - /matcher")
    print("  - /viewer")
    print("  - /cluster")
    print("  - /shop")
    print("  - /labeler")

    yield

    # Shutdown
    print("Shutting down Image Dataset Management System...")


app = FastAPI(
    title="Image Dataset Management System",
    description="Unified backend for image classification, matching, viewing, and labeling",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Include routers for each module with module-specific prefixes
# Each module gets its own API namespace to avoid route conflicts
# Frontend routes (/, /matcher, etc.) remain the same

app.include_router(classifier_router, prefix="/api/classifier", tags=["classifier"])
app.include_router(matcher_router, prefix="/api/matcher", tags=["matcher"])
app.include_router(viewer_router, prefix="/api/viewer", tags=["viewer"])
app.include_router(cluster_router, prefix="/api/cluster", tags=["cluster"])
app.include_router(shop_router, prefix="/api/shop", tags=["shop"])
app.include_router(text_labeler_router, prefix="/api/labeler", tags=["text_labeler"])


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "modules": [
            "classifier",
            "matcher",
            "viewer",
            "cluster",
            "shop",
            "text_labeler",
        ],
    }


# Mount static files for frontend (must be last)
app.mount("/", StaticFiles(directory="cleaner/dist", html=True), name="static")


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        reload_dirs=["handlers", "utils"],
    )
