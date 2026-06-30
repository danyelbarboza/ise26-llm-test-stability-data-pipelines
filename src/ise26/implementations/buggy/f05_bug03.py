"""Buggy variant for F05 that rejects extra columns."""

from __future__ import annotations

from typing import Any

import pandas as pd

from ..correct import *  # noqa: F401,F403
from .. import correct as correct_module


def validate_schema(df: pd.DataFrame, schema: dict[str, str]) -> dict[str, Any]:
    """Return a buggy validation result that rejects extra columns.

    This version validates missing columns and type mismatches, but it also
    treats additional columns as an error even though extras should be allowed.

    Args:
        df: DataFrame to validate.
        schema: Mapping from column name to expected logical type.

    Returns:
        A dictionary with buggy schema-validation results.
    """

    # BUG: Extra columns incorrectly invalidate the DataFrame.
    missing_columns: list[str] = []
    type_errors: list[dict[str, str]] = []

    for column_name, expected_type in schema.items():
        normalized_expected_type = correct_module._normalize_expected_type(expected_type)

        if column_name not in df.columns:
            missing_columns.append(column_name)
            continue

        actual_type = correct_module._infer_series_type(df[column_name])
        if not correct_module._matches_expected_type(actual_type, normalized_expected_type):
            type_errors.append(
                {
                    "column": column_name,
                    "expected": normalized_expected_type,
                    "actual": actual_type,
                }
            )

    extra_columns = [column_name for column_name in df.columns if column_name not in schema]
    for column_name in extra_columns:
        type_errors.append(
            {
                "column": column_name,
                "expected": "not_present",
                "actual": "extra_column",
            }
        )

    return {
        "valid": not missing_columns and not type_errors,
        "missing_columns": missing_columns,
        "type_errors": type_errors,
    }
