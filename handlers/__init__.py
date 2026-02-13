"""
Handlers package for the Image Dataset Management System.

Each handler module corresponds to a specific view in the frontend.
"""

from .classifier import router as classifier_router
from .cluster import router as cluster_router
from .matcher import router as matcher_router
from .shop import router as shop_router
from .text_labeler import router as text_labeler_router
from .viewer import router as viewer_router

__all__ = [
    "classifier_router",
    "matcher_router",
    "viewer_router",
    "cluster_router",
    "shop_router",
    "text_labeler_router",
]
