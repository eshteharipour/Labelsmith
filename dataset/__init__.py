"""
Refactored dataset management package.

This package provides clean, DRY implementations for dataset handling:
- classifier: Image classification with status management
- matcher: Product matching datasets
- viewer: Image similarity viewing
- cluster: Clustered image viewing
- eda: Exploratory data analysis utilities
- core: Common utilities (JSON, state, DataFrame ops)

Usage:
    from dataset import classifier, matcher, viewer, cluster, eda

    # Classifier
    df, clf_dict, orig_dict, state_file, state, default_image, statuses, cluster_col = (
        classifier.read_dataset()
    )

    # Matcher
    df, state, state_file, default_image = matcher.read_dataset(
        matcher.DatasetEnum.Train,
        SHOW_REVIEWD=False,
        show_matchings="all",
    )

    # Viewer
    df, state, state_file, default_image = viewer.read_dataset()

    # Cluster
    df, state_file, state, default_image, cluster_col = cluster.read_dataset()
"""

from . import classifier, cluster, core, eda, matcher, viewer

__all__ = [
    "classifier",
    "matcher",
    "viewer",
    "cluster",
    "eda",
    "core",
]

__version__ = "2.0.0"
