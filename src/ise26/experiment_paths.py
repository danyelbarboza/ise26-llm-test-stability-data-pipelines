"""Helpers for resolving model-specific experiment paths."""

from __future__ import annotations

import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def normalize_model_key(model_name: str) -> str:
    """Convert a model name into a filesystem-safe model key.

    Args:
        model_name: Raw model name from configuration or CLI input.

    Returns:
        A normalized key suitable for directory names.
    """

    normalized = re.sub(r"[^A-Za-z0-9]+", "_", model_name.strip().lower())
    return normalized.strip("_")


def resolve_generated_tests_root(model_name: str) -> Path:
    """Return the root directory for generated tests of one model."""

    return PROJECT_ROOT / "experiments" / "generated_tests" / normalize_model_key(model_name)


def resolve_results_root(model_name: str) -> Path:
    """Return the root directory for results of one model."""

    return PROJECT_ROOT / "results" / "by_model" / normalize_model_key(model_name)


def resolve_comparison_root() -> Path:
    """Return the directory used for cross-model comparison assets."""

    return PROJECT_ROOT / "paper_assets" / "model_comparison"


def resolve_model_config_path(model_name: str) -> Path:
    """Return the expected config path for a model name."""

    return PROJECT_ROOT / "experiments" / "config" / f"{normalize_model_key(model_name)}.json"
