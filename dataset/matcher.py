"""
Matcher dataset handler.

Handles product matching datasets with various filtering options.
"""

import os
from typing import Literal, Tuple

import pandas as pd
from prod2vec.dataset.settings import (
    DatasetEnum,
    LCSCIseeCLip,
    LIPDataset,
    get_default_image,
)
from prod2vec.dataset.settings import read_dataset as _read_dataset
from prod2vec.dataset.settings import save_csv

from .core import get_state_file_path, init_state_file, prepare_dataframe_for_web
from .eda import must_be_different_categories, must_have_farsi, sort_by_blur


def read_dataset(
    DATASET: DatasetEnum,
    SHOW_REVIEWD: bool,
    show_matchings: Literal["all", "true", "false"],
) -> Tuple[pd.DataFrame, dict, str, str]:
    """
    Read and prepare matcher dataset.

    Args:
        DATASET: Which dataset to load
        SHOW_REVIEWD: Whether to show previously reviewed items
        show_matchings: Filter by matching status

    Returns:
        Tuple of (df, state, state_file, default_image)
    """
    default_image = get_default_image()
    state_file = get_state_file_path("matcher")

    # lip = LIPDataset()
    # lcsc = LCSCIseeCLip
    df = _read_dataset(DATASET, SHOW_REVIEWD, show_matchings)

    # ========================================================================
    # EDA FILTERING (only for EDA dataset)
    # ========================================================================

    if DATASET == DatasetEnum.EDA:
        # Import EDA functions only when needed

        # df = must_have_farsi(df)
        # df = must_be_different_categories(df)
        df = sort_by_blur(df)

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

    df = df[lip.matching_cols_subset + ["matching"]]
    df = df.drop_duplicates(subset=lip.matching_cols_subset, keep="last")
    df = df.reset_index(drop=True)

    save_csv(df, path)


def save_dataset(df: pd.DataFrame) -> None:
    """
    Save dataset to humaneval path.

    Args:
        df: DataFrame to save
    """
    lcsc = LCSCIseeCLip
    path = lcsc.humaneval
    _save_dataset(df, path)
