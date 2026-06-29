"""Buggy variant for F05 that ignores missing columns."""

from __future__ import annotations

from typing import Any

import pandas as pd

from ..correct import *  # noqa: F401,F403
from .. import correct as correct_module


def validate_schema(df: pd.DataFrame, schema: dict[str, str]) -> dict[str, Any]:
    """Return a buggy validation result that ignores missing columns.

    This version still checks logical types for columns that exist, but it
    never reports missing required columns.

    Args:
        df: DataFrame to validate.
        schema: Mapping from column name to expected logical type.

    Returns:
        A dictionary with buggy schema-validation results.
    """

    # BUG: Missing columns are silently ignored.
    type_errors: list[dict[str, str]] = []

    for column_name, expected_type in schema.items():
        normalized_expected_type = correct_module._normalize_expected_type(expected_type)

        if column_name not in df.columns:
            continue

        actual_type = correct_module._infer_series_type(df[column_name])
        if not correct_module._matches_expected_type(actual_type, normalized_expected_type):
            type_errors.append(
                {
                    "column": column_name,
                    "expected_type": normalized_expected_type,
                    "actual_type": actual_type,
                }
            )

    return {
        "valid": not type_errors,
        "missing_columns": [],
        "type_errors": type_errors,
    }
