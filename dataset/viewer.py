"""
Viewer dataset handler.

Handles image similarity viewing datasets.
"""

import os
from typing import Tuple

import pandas as pd

from .core import get_state_file_path, init_state_file, prepare_dataframe_for_web
from .settings import LCSCIseeCLip, LIPDataset, get_default_image, save_csv


def read_dataset() -> Tuple[pd.DataFrame, dict, str, str]:
    """
    Read and prepare viewer dataset.

    Returns:
        Tuple of (df, state, state_file, default_image)
    """
    default_image = get_default_image()
    state_file = get_state_file_path("viewer")

    lip = LIPDataset()

    # Load dataset
    df = lip.all_train()

    # ========================================================================
    # FILTERING OPTIONS - Uncomment as needed
    # ========================================================================

    # Filter: Different nearest neighbors
    # df = df[df["rn18_l2"] != df["rn18_ip"]]

    # Filter: Low L2 distance
    # df = df[df["rn18_l2_d"].astype(float) < 0.05]
    # df = df.sort_values("rn18_l2_d", ascending=False)

    # Filter: High inner product distance
    # df = df[df["rn18_ip_d"].astype(float) > 0.95]
    # df = df.sort_values("rn18_ip_d", ascending=False)

    # Sort by inner product distance
    # df = df.dropna(subset=["path"]).sort_values("rn18_ip_d", ascending=False)

    # Sort by blur
    # df = df.dropna(subset=["path"]).sort_values("blur", ascending=False)
    # df = df.dropna(subset=["path"]).sort_values("blur", ascending=True)

    # ========================================================================
    # DEFAULT FILTERING
    # ========================================================================

    # Keep only images with valid paths
    df = df[df["path"].astype(bool)]
    df = df.dropna(subset=["path"])

    # Random shuffle for variety
    df = df.sample(frac=1, ignore_index=True, random_state=362)

    # ========================================================================
    # PREPARE FOR WEB
    # ========================================================================

    df = prepare_dataframe_for_web(df)

    # Load or create state
    state = init_state_file(state_file)

    return df, state, state_file, default_image


def _save_dataset(df: pd.DataFrame, path: str) -> None:
    """
    Save dataset with deduplication.

    Args:
        df: DataFrame to save
        path: Path to save to
    """
    lip = LIPDataset()

    if os.path.exists(path):
        prev_df = lip.read_csv(path)
        df = pd.concat([prev_df, df], ignore_index=True)
    else:
        df = df.copy()

    df = df[["path"]]
    df = df.drop_duplicates(subset=["path"], keep="last")
    df = df.reset_index(drop=True)

    save_csv(df, path)


def save_dataset(df: pd.DataFrame) -> None:
    """
    Save dataset to OK dataset path.

    Args:
        df: DataFrame to save
    """
    lcsc = LCSCIseeCLip
    path = lcsc.ok_dataset
    _save_dataset(df, path)
