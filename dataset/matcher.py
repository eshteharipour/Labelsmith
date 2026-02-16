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
    save_csv,
)

from .core import get_state_file_path, init_state_file, prepare_dataframe_for_web


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

    lip = LIPDataset()
    lcsc = LCSCIseeCLip

    # ========================================================================
    # DATASET SELECTION
    # ========================================================================

    if DATASET == DatasetEnum.Train:
        print("Loading train dataset")
        df = lip.train_matchings()

    elif DATASET == DatasetEnum.Val:
        print("Loading validation dataset")
        df = lip.valid_matchings()

    elif DATASET == DatasetEnum.Test:
        print("Loading test dataset")
        df = lip.test_matchings()

    elif DATASET == DatasetEnum.TrVT:
        print("Loading train, validation and test dataset")
        df = lip.all_matchings()

    elif DATASET == DatasetEnum.LLM:
        print("Loading llm evaluated dataset")
        df = lip.llm()

    elif DATASET == DatasetEnum.Human:
        print("Loading human reviewed dataset")
        df = lip.humaneval()

    elif DATASET == DatasetEnum.Compare:
        # Special dataset - Comparing LLM different responses
        print("Loading double llm reviewed dataset")
        dfa = lip.llm("geminiflash2_v5")
        # dfb = lip.llm("gemma3_v4")
        dfb = lip.humaneval()
        df = lip.compare(dfa, dfb)

    elif DATASET == DatasetEnum.Output:
        path = os.path.join(lcsc.output_path, "bin_dino_vits8liphumaneval_binary.csv")
        df = lip.read_csv(path)
        df = lip._split_matchings(df)
        df = df.drop(columns=["response2"])

        # Only wrong answers:
        if True:
            # model_matches = df["response"].apply(
            #     lambda x: (
            #         {"not": False, "MATCH": True}[x.split(" ")[0]]
            #         if x and pd.notna(x)
            #         else x
            #     )
            # )
            model_matches = df["model_matching"]
            df = df[df["matching"] != model_matches]

    elif DATASET == DatasetEnum.EDA:
        print("Loading EDA dataset")
        df = lip.valid_matchings()
        df = lip.partno_matching(df)

    else:
        raise ValueError(f"Unknown dataset: {DATASET}")

    print(f"Length of dataset: {len(df)}")

    # ========================================================================
    # EDA FILTERING (only for EDA dataset)
    # ========================================================================

    if DATASET == DatasetEnum.EDA:
        # Import EDA functions only when needed
        from .eda import must_be_different_categories, must_have_farsi, sort_by_blur

        # df = must_have_farsi(df)
        # df = must_be_different_categories(df)
        df = sort_by_blur(df)

    # ========================================================================
    # MATCHING FILTER
    # ========================================================================

    if show_matchings.strip().lower() in ["true", "false"]:
        df = df[
            (
                df["matching"] == True
                if show_matchings.strip().lower() == "true"
                else False
            )
        ]
        print(f"Length of dataset with {show_matchings} matchings: {len(df)}")

    # ========================================================================
    # REMOVE REVIEWED (if requested)
    # ========================================================================

    if SHOW_REVIEWD == False:
        he = lip.humaneval()
        alt_he = he.copy()
        alt_he = alt_he.rename(columns=lip.reverse_source_target_mapping)
        df = pd.concat([he, he, alt_he, alt_he, df]).reset_index(drop=True)
        df = df.drop_duplicates(subset=lip.matching_cols_subset, keep=False)
        print(f"Length of dataset after removing reviewed: {len(df)}")

    # ========================================================================
    # SORTING
    # ========================================================================

    if (
        DATASET != DatasetEnum.Output
        and DATASET != DatasetEnum.Human
        and DATASET != DatasetEnum.EDA
    ):
        df = df.sort_values(by=["source_name", "target_name"])

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
