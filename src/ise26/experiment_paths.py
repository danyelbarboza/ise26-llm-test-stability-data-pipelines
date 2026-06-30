"""Helpers for resolving model- and experiment-specific paths."""

from __future__ import annotations

import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LEGACY_EXPERIMENT_ID = "exp_6_functions"


def normalize_model_key(model_name: str) -> str:
    """Convert a model name into a filesystem-safe model key.

    Args:
        model_name: Raw model name from configuration or CLI input.

    Returns:
        A normalized key suitable for directory names.
    """

    normalized = re.sub(r"[^A-Za-z0-9]+", "_", model_name.strip().lower())
    return normalized.strip("_")


def normalize_experiment_id(experiment_id: str) -> str:
    """Convert an experiment identifier into a filesystem-safe directory name.

    Args:
        experiment_id: Raw experiment identifier from the CLI or configuration.

    Returns:
        A normalized key suitable for directory names.
    """

    normalized = re.sub(r"[^A-Za-z0-9]+", "_", experiment_id.strip().lower())
    return normalized.strip("_")


def resolve_generated_tests_root(model_name: str, experiment_id: str | None = None) -> Path:
    """Return the root directory for generated tests of one model."""

    model_key = normalize_model_key(model_name)
    if experiment_id:
        return PROJECT_ROOT / "experiments" / "generated_tests" / normalize_experiment_id(experiment_id) / model_key

    return PROJECT_ROOT / "experiments" / "generated_tests" / model_key


def resolve_results_root(model_name: str, experiment_id: str | None = None) -> Path:
    """Return the root directory for results of one model."""

    model_key = normalize_model_key(model_name)
    if experiment_id:
        return PROJECT_ROOT / "results" / "by_experiment" / normalize_experiment_id(experiment_id) / "by_model" / model_key

    return PROJECT_ROOT / "results" / "by_model" / model_key


def resolve_comparison_root(experiment_id: str | None = None) -> Path:
    """Return the directory used for cross-model comparison assets."""

    if experiment_id:
        return PROJECT_ROOT / "paper_assets" / normalize_experiment_id(experiment_id) / "model_comparison"

    return PROJECT_ROOT / "paper_assets" / "model_comparison"


def resolve_model_config_path(model_name: str, experiment_id: str | None = None) -> Path:
    """Return the expected config path for a model name."""

    model_key = normalize_model_key(model_name)
    if experiment_id:
        experiment_suffix = normalize_experiment_id(experiment_id).removeprefix("exp_")
        return PROJECT_ROOT / "experiments" / "config" / f"{model_key}_{experiment_suffix}.json"

    return PROJECT_ROOT / "experiments" / "config" / f"{model_key}.json"


def resolve_metadata_root(experiment_id: str | None = None) -> Path:
    """Return the metadata directory for the selected experiment."""

    if experiment_id:
        return PROJECT_ROOT / "src" / "ise26" / "metadata" / normalize_experiment_id(experiment_id)

    return PROJECT_ROOT / "src" / "ise26" / "metadata" / DEFAULT_LEGACY_EXPERIMENT_ID


def resolve_functions_metadata_path(experiment_id: str | None = None) -> Path:
    """Return the functions metadata path for the selected experiment."""

    return resolve_metadata_root(experiment_id) / "functions.json"


def resolve_bugs_metadata_path(experiment_id: str | None = None) -> Path:
    """Return the bugs metadata path for the selected experiment."""

    return resolve_metadata_root(experiment_id) / "bugs.json"
