"""Buggy variant for F05 that ignores type mismatches."""

from __future__ import annotations

from typing import Any

import pandas as pd

from ..correct import *  # noqa: F401,F403
from .. import correct as correct_module


def validate_schema(df: pd.DataFrame, schema: dict[str, str]) -> dict[str, Any]:
    """Return a buggy validation result that ignores type errors.

    This version correctly reports missing columns, but it never flags logical
    type mismatches for columns that are present.

    Args:
        df: DataFrame to validate.
        schema: Mapping from column name to expected logical type.

    Returns:
        A dictionary with buggy schema-validation results.
    """

    # BUG: Type mismatches are not reported.
    missing_columns: list[str] = []

    for column_name, expected_type in schema.items():
        correct_module._normalize_expected_type(expected_type)

        if column_name not in df.columns:
            missing_columns.append(column_name)

    return {
        "valid": not missing_columns,
        "missing_columns": missing_columns,
        "type_errors": [],
    }
