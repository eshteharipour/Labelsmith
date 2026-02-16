"""
EDA (Exploratory Data Analysis) utilities.

Provides filtering and analysis functions for dataset exploration.
"""

import pandas as pd

from .settings import LIPDataset


def must_have_farsi(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter to keep only rows with Farsi/Persian text.

    Requires: yumbox.nlp.UnicodeRanges

    Args:
        df: DataFrame with source_name and target_name columns

    Returns:
        Filtered DataFrame containing only rows with Farsi text
    """
    from yumbox.nlp import UnicodeRanges

    r = UnicodeRanges.regex_from_range(UnicodeRanges.persian_letters_ranges)
    fltr = df["source_name"].str.contains(r, regex=True, na=False)
    fltr = fltr | df["target_name"].str.contains(r, regex=True, na=False)
    df = df[fltr]
    print(f"Length of dataset with must have Farsi: {len(df)}")
    return df


def must_be_different_categories(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter to keep only rows where source and target have different categories.

    Args:
        df: DataFrame with source and target items

    Returns:
        Filtered DataFrame with different categories
    """
    lip = LIPDataset()
    all_df = lip.all()
    df = lip.matching_categories(all_df, df)

    fltr = df["source_category"] != df["target_category"]
    fltr = fltr & df["source_category"].notna() & df["source_category"].astype(bool)
    fltr = fltr & df["target_category"].notna() & df["target_category"].astype(bool)

    df = df[fltr]
    print(f"Length of dataset with different categories: {len(df)}")
    return df


def sort_by_blur(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sort dataset by combined blur score of source and target images.

    Higher blur values appear first.

    Args:
        df: DataFrame with source_image and target_image columns

    Returns:
        Sorted DataFrame
    """
    lip = LIPDataset()
    all_df = lip.all()
    d = dict(zip(all_df["path"], all_df["blur"]))

    a = df["source_image"].map(d)
    b = df["target_image"].map(d)
    df.loc[:, "blur"] = a + b
    df = df.sort_values(by="blur", ascending=False)

    return df
