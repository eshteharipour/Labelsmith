"""
Cluster dataset handler.

Handles clustered image viewing datasets.
"""

import os
from typing import Tuple

import pandas as pd

from .core import get_state_file_path, init_state_file, prepare_dataframe_for_web
from .settings import LCSCIseeCLip, LIPDataset, get_default_image


def only_unique_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Keep only unique (cluster_id, name) pairs.

    For text-only model matchers, we want to show unique names per cluster.

    Args:
        df: DataFrame with cluster_id and name columns

    Returns:
        Filtered DataFrame with unique names per cluster
    """
    lip = LIPDataset()

    cleaned_df = []
    seen = set()

    for i, r in df.iterrows():
        t = (r["cluster_id"], r["name"])
        if t not in seen:
            seen.add(t)
            cleaned_df.append(r)

    df = pd.DataFrame(cleaned_df, columns=df.columns)

    # Rebuild index sizes after filtering
    df = lip.add_csize_col(df)

    return df


def read_dataset() -> Tuple[pd.DataFrame, str, dict, str, str]:
    """
    Read and prepare cluster dataset.

    Returns:
        Tuple of (df, state_file, state, default_image, cluster_col)
    """
    default_image = get_default_image()
    state_file = get_state_file_path("cluster")
    cluster_col = "cluster_id"

    lip = LIPDataset()
    lcsc = LCSCIseeCLip

    # ========================================================================
    # LOAD DATASET
    # ========================================================================

    dataset_path = "default_experiment_model_devel_lip_valid_partno_binary.csv"
    print(f"Loading dataset {dataset_path}")
    path = os.path.join(lcsc.output_path, dataset_path)
    df = lip.read_csv(path)

    # ========================================================================
    # CONVERT MATCHINGS TO CLUSTERS
    # ========================================================================

    df = lip.matchings2clusters(df, matching_col="model_matching", threshold=None)

    # ========================================================================
    # FILTERING
    # ========================================================================

    # Convert cluster_id to int and sort
    df.loc[:, "cluster_id"] = df["cluster_id"].astype(int)
    df = df.sort_values(by="cluster_id")

    # Only show unique names (text only model matcher)
    df = only_unique_names(df)

    # Only show large clusters
    df = df[df["csize"] > 1]

    # ========================================================================
    # PREPARE FOR WEB
    # ========================================================================

    df = prepare_dataframe_for_web(df)

    # Load or create state
    state = init_state_file(state_file)

    return (
        df,
        state_file,
        state,
        default_image,
        cluster_col,
    )
