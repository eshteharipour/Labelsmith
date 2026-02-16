"""
Classifier dataset handler.

Handles image classification with status management and filtering.
"""

import ast
import functools
import logging
import os
import random
import string
from itertools import repeat
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

from .core import get_state_file_path, init_state_file, prepare_dataframe_for_web
from .core import read_json as _read_json
from .core import save_json as _save_json
from .settings import LCSCIseeCLip, LIPDataset, get_default_image

STATUSES = ["bad", "log", "ood", "gen", "half_logo", "blurry", "ok"]
logger = logging.getLogger("ElecNet")


def status_sorter(x):
    """Sort statuses by predefined order."""
    try:
        return STATUSES.index(x)
    except ValueError:
        return float("inf")


def sort_json(d: dict) -> dict:
    """Sort selected images in JSON by status."""
    if "selected_images" in d:
        keys = sorted(
            d["selected_images"],
            key=lambda x: ((status_sorter(d["selected_images"][x]), x)),
        )
        d["selected_images"] = {k: d["selected_images"][k] for k in keys}
    return d


def reduce_json_basename(d: dict) -> dict:
    """Remove duplicate basenames from selected images."""
    if "selected_images" in d:
        seen = set()
        d["selected_images"] = {
            k: v
            for k, v in d["selected_images"].items()
            if (bn := os.path.basename(k)) not in seen and not seen.add(bn)
        }
    return d


def read_json(path: str):
    d = _read_json(path)

    d = reduce_json_basename(d)
    d = sort_json(d)
    return d


def save_json(path: str, d: dict):
    d = reduce_json_basename(d)
    d = sort_json(d)

    _save_json(path, d)


def load_text_dumps(state: dict) -> dict:
    """
    Load text dumps into state.

    Reads classification files and merges them into state.
    """
    lcsc = LCSCIseeCLip

    paths_list = [
        lcsc.bad_images(),
        lcsc.logo_images(),
        lcsc.ood_products(),
        lcsc.generic_images(),
        lcsc.half_logo_images(),
        lcsc.blurry_images(),
        lcsc.ok_images(),
    ]

    for paths, status in zip(paths_list, STATUSES):
        d = {x: status for x in paths}
        state["selected_images"].update(d)

    state = reduce_json_basename(state)
    state = sort_json(state)
    return state


def save_text_dumps(state: dict) -> None:
    """
    Save text dumps from state.

    Writes classifications to separate files by status.
    """
    lcsc = LCSCIseeCLip

    paths_list = [
        lcsc.bad_images(),
        lcsc.logo_images(),
        lcsc.ood_products(),
        lcsc.generic_images(),
        lcsc.half_logo_images(),
        lcsc.blurry_images(),
        lcsc.ok_images(),
    ]

    write_funcs_list = [
        lcsc.write_bad_images,
        lcsc.write_logo_images,
        lcsc.write_ood_products,
        lcsc.write_generic_images,
        lcsc.write_half_logo_images,
        lcsc.write_blurry_images,
        lcsc.write_ok_images,
    ]

    # Remove duplicates across categories (keep in first category)
    for i, src in enumerate(paths_list):
        for tgt in paths_list[i + 1 :]:
            to_remove = set(src).intersection(set(tgt))
            for tr in to_remove:
                paths_list[i + 1].remove(tr)

    # Write previous images
    for status, prev_images, write_func in zip(STATUSES, paths_list, write_funcs_list):
        images = list(sorted(set(prev_images)))
        write_func(images)

    # Write current state
    for status, write_func in zip(STATUSES, write_funcs_list):
        paths = [k for k, v in state["selected_images"].items() if v == status]
        paths = [p for p in paths if p]
        images = list(sorted(set(paths)))
        write_func(images)


def init() -> Tuple[str, dict, str, List[str]]:
    """
    Initialize classifier state.

    Returns:
        Tuple of (state_file, state, default_image, statuses)
    """
    state_file = get_state_file_path("classifier")

    if os.path.exists(state_file):
        state = read_json(state_file)
        state_statuses = list(state["selected_images"].values())
    else:
        state_statuses = []
        state = {"selected_images": {}, "settings": {"lastPage": 0}}

    state = load_text_dumps(state)
    save_json(state_file, state)

    statuses = list(sorted(set(STATUSES + state_statuses), key=status_sorter))
    default_image = get_default_image()

    return state_file, state, default_image, statuses


# ============================================================================
# FILTERS - Keep all existing filters with comments
# ============================================================================


def fltr(func):
    """Decorator for filter functions that resets page and assigns unique IDs."""

    @functools.wraps(func)
    def wrapper(df: pd.DataFrame, state: dict):
        state["settings"]["lastPage"] = 0

        # uid = func.__name__
        uid = "".join(random.sample(string.ascii_lowercase, 5))
        df.index = np.array([uid + x for x in df.index.values])
        # assigning to index resets it's name!
        df.index.name = "id"

        # df = df[df.basename.isin(df.basename.unique())]

        return func(df, state)

    return wrapper


@fltr
def site_a(df: pd.DataFrame, state: dict):
    """Filter for site A (LCSC copier)."""
    # 20 -> LCSC copier!
    df = df[df["site_id"] == "20"]  # page 7
    return df


@fltr
def site_b(df: pd.DataFrame, state: dict):
    """Filter for site B (Skytech)."""
    # 165 -> Skytech
    df = df[df["site_id"] == "165"]
    return df


@fltr
def value_counts(df: pd.DataFrame, state: dict):
    """Sort by basename frequency."""
    df = df[df["basename"].notna() & df["basename"].astype(bool)]
    df = df[df["path"].notna() & df["path"].astype(bool)]
    vc = df["basename"].value_counts()
    df["vc"] = df["basename"].map(vc)
    df = df.sort_values("vc", ascending=False)
    return df


@fltr
def sorter(df: pd.DataFrame, state: dict):
    """Sort by cluster size, cluster ID, basename, and name."""
    df = df.sort_values(["csize", "cluster_id", "basename", "name"], ascending=False)
    return df


@fltr
def cluster(df: pd.DataFrame, state: dict):
    """Explode cluster nearest neighbors."""
    df["resnet_1nn"] = df["resnet_1nn"].apply(
        lambda x: (
            ast.literal_eval(x.replace("\n", ",")) if pd.notna(x) and bool(x) else x
        )
    )
    df["resnet_1nn_d"] = df["resnet_1nn_d"].apply(
        lambda x: (
            ast.literal_eval(",".join(x.split()))
            if pd.notna(x) and bool(x)
            else float("nan")
        )
    )
    df = df.sort_values("resnet_1nn_d", ascending=False)
    df = df[df["basename"].notna()]
    df = df[df["resnet_1nn"].notna()]
    bn2row = dict(zip(df["basename"], df.to_dict(orient="index").values()))
    df = df.explode("resnet_1nn")
    df = df["resnet_1nn"].map(bn2row)
    df = df.dropna()
    df = pd.DataFrame(df.values.tolist(), index=df.index)
    df["name_lower"] = df["name"].astype(str).str.lower()
    df = df.drop_duplicates(subset=["basename", "name_lower"])
    df = df.reset_index(drop=True)
    return df


@fltr
def dbscan(df: pd.DataFrame, state: dict):
    """Sort by DBSCAN cluster with selected images first."""
    # df = df[df["dbscan"] == "-1"].reset_index(drop=True)
    order = dict(zip(state["selected_images"], repeat(0)))
    df["sort"] = df["basename"].map(order)
    df = df.sort_values(["sort", "dbscan"])
    df = df.drop(columns=["sort"])
    # df = df.reset_index(drop=True)
    return df


@fltr
def mymapred(df: pd.DataFrame, state: dict):
    """Map-reduce: keep one per basename, sorted by frequency."""
    df.loc[:, "bn_freq"] = df["basename"].map(df["basename"].value_counts().to_dict())
    df = df.sort_values("bn_freq", ascending=False)
    # df = df.sort_values("csize", ascending=False)
    df = df.drop_duplicates("basename")
    return df


def logo_profiling(df: pd.DataFrame):
    """Profile logos using ResNet18 features."""
    import logging

    from prod2vec.dataset import BFG, CACHE_DIR
    from prod2vec.evaluation.factory import resnet18_feats
    from prod2vec.evaluation.tools import (
        build_index,
        image_feats,
        normalize_vector,
        reconstruct_original_index,
        topk,
    )

    BFG["cache_dir"] = CACHE_DIR

    lip = LIPDataset()
    ood_df = lip.logo()

    q_feats = resnet18_feats(ood_df)
    q_feats, missing = image_feats(ood_df, q_feats)
    print(f"Length of logo missing pictures: {len(missing)}")

    logo_prof = np.sum(q_feats, axis=0)
    logo_prof = np.expand_dims(logo_prof, 0)
    logo_prof = normalize_vector(logo_prof)

    # Filtering DF so I don't have to use reconstruct_original_index
    df = df[df["path"].astype(bool) & df["path"].notna()]

    c_feats = resnet18_feats(df)
    c_feats, missing = image_feats(df, c_feats)
    c_feats = normalize_vector(c_feats)

    print(f"Length of dataset missing pictures: {len(missing)}")
    # To my wonder, FAISS matches the np.inf arrays as most similar!!
    # embed_size = c_feats[0].shape[-1]
    # c_feats = reconstruct_original_index(
    #     c_feats, missing, fill_value=np.array([np.inf] * embed_size)
    # )

    index = build_index(c_feats)
    d, i = topk(index, "search", logo_prof, k=1000)
    df = df[df.index.isin(i)]
    return df


def get_dataset():
    """Get main dataset for classification."""
    lip = LIPDataset()
    df = lip.all()
    # df = lip.read_csv(
    #     "/home/sx/Code/asenpp/datasets/LCSC_ISEE_clip/post_playground/dbscan_resnet18.csv"
    # )
    return df


def get_ood_dataset():
    """Get out-of-distribution dataset."""
    lip = LIPDataset()
    # lip.bad()
    df = lip.logo()
    # lip.ood_products()
    # lip.generic()
    # lip.half_logo()
    # lip.blurry()
    # lip.ood()
    return df


def group_dataset(df: pd.DataFrame, cluster_col: str):
    """Group dataset by cluster column."""
    return df.sort_values(cluster_col)


def group_query_candidate(cluster_col: str):
    """Group query and candidate sets by cluster."""
    lip = LIPDataset()
    q = lip._valid_qm()
    c = lip._valid_c()

    indices = q[cluster_col].unique()
    c = c[c[cluster_col].isin(indices)]

    sort_col_name = "_internal_sort"
    q.loc[:, sort_col_name] = np.array([1] * len(q))
    c.loc[:, sort_col_name] = np.array([2] * len(c))

    df = pd.concat([q, c]).reset_index(drop=True)
    df = df.sort_values([cluster_col, sort_col_name])
    return df


def read_dataset():
    """
    Read and prepare classifier dataset.

    Returns:
        Tuple of (df, clf_dict, orig_dict, state_file, state, default_image, statuses, cluster_col)
    """
    state_file, state, default_image, statuses = init()

    lip = LIPDataset()

    # Create dictionary for fast lookup from matching dataset
    clf_dict = lip.train_matchings()
    clf_dict.index = clf_dict.index.astype(str)
    clf_dict.index.name = "id"
    clf_dict = clf_dict.to_dict(orient="records")
    clf_dict = {k["path"]: k for k in clf_dict}

    cluster_col = None
    df = get_dataset()
    cluster_col = "dbscan"
    # df = group_dataset(df, cluster_col)
    cluster_col = "cluster_id"
    # df = group_query_candidate(cluster_col)

    # Prepare for web display
    df = prepare_dataframe_for_web(df)

    # Create original dictionary for lookup
    orig_dict = df.to_dict(orient="records")
    orig_dict = {k["path"]: k for k in orig_dict}

    # ========================================================================
    # FILTERS - Uncomment the ones you want to use
    # ========================================================================
    # df = site_a(df, state)
    # df = site_b(df, state)
    # df = value_counts(df, state)
    # df = sorter(df, state)
    # df = cluster(df, state)
    # df = dbscan(df, state)
    # df = mymapred(df, state)
    df = df.dropna(subset=["path"]).sort_values("blur", ascending=True)

    # ========================================================================
    # OOD DATASETS - Uncomment to use
    # ========================================================================
    # df = get_ood_dataset()
    # df = logo_profiling(df)

    return (
        df,
        clf_dict,
        orig_dict,
        state_file,
        state,
        default_image,
        statuses,
        cluster_col,
    )
