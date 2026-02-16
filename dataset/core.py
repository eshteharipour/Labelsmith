"""
Core utilities for dataset management.

This module contains common functionality shared across all dataset handlers:
- JSON file operations
- State management
- DataFrame utilities
- Path handling
"""

import json
import os
from typing import Any, Dict, Optional, Tuple

import pandas as pd


def read_json(path: str) -> dict:
    """
    Read JSON file and return dictionary.

    Args:
        path: Path to JSON file

    Returns:
        Dictionary containing JSON data
    """
    with open(path, "r", encoding="utf-8") as fd:
        d = json.load(fd)
    return d


def save_json(path: str, d: dict) -> None:
    """
    Save dictionary to JSON file with pretty formatting.

    Args:
        path: Path to save JSON file
        d: Dictionary to save
    """
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)


def convert_nan_to_none(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert NaN values to None for JSON compatibility.

    Fixes float data on JSON dumps issue by replacing NaN with None.

    Args:
        df: DataFrame to process

    Returns:
        DataFrame with NaN replaced by None
    """
    df = df.replace({float("nan"): None})
    return df


def prepare_dataframe_for_web(
    df: pd.DataFrame,
    index_name: str = "id",
    convert_nans: bool = True,
    assert_unique: bool = True,
) -> pd.DataFrame:
    """
    Prepare DataFrame for web display.

    Common operations:
    - Convert NaN to None (for JSON)
    - Convert index to string
    - Set index name
    - Assert unique index

    Args:
        df: DataFrame to prepare
        index_name: Name for the index column
        convert_nans: Whether to convert NaN to None
        assert_unique: Whether to assert index uniqueness

    Returns:
        Prepared DataFrame
    """
    if convert_nans:
        df = convert_nan_to_none(df)

    df.index = df.index.astype(str)
    df.index.name = index_name

    if assert_unique:
        assert df.index.is_unique, "DataFrame index must be unique"

    return df


def init_state_file(
    state_file: str, default_state: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Initialize or load state file.

    Args:
        state_file: Path to state file
        default_state: Default state if file doesn't exist

    Returns:
        State dictionary
    """
    if default_state is None:
        default_state = {"settings": {"lastPage": 0}}

    if os.path.isfile(state_file):
        state = read_json(state_file)
    else:
        state = default_state.copy()
        save_json(state_file, state)

    return state


def ensure_artifacts_dir(base_path: str = "/home/sx/Code/asenpp/artifacts") -> str:
    """
    Ensure artifacts directory exists.

    Args:
        base_path: Base path for artifacts directory

    Returns:
        Path to artifacts directory
    """
    os.makedirs(base_path, exist_ok=True)
    return base_path


def get_state_file_path(module_name: str, artifacts_dir: Optional[str] = None) -> str:
    """
    Get standard path for module state file.

    Args:
        module_name: Name of the module (e.g., 'classifier', 'matcher')
        artifacts_dir: Optional custom artifacts directory

    Returns:
        Full path to state file
    """
    if artifacts_dir is None:
        artifacts_dir = ensure_artifacts_dir()

    return os.path.join(artifacts_dir, f"{module_name}_state.json")
