"""Buggy variant for F09 that fills missing values with zero."""

from __future__ import annotations

import pandas as pd

from ..correct import *  # noqa: F401,F403


def cap_outliers_iqr(
    df: pd.DataFrame,
    value_col: str = "amount",
    output_col: str = "amount_capped",
) -> pd.DataFrame:
    """Return a buggy capped column that replaces missing values with zero."""

    # BUG: Missing values are converted to zero instead of staying missing.
    result = df.copy(deep=True)
    numeric_values = pd.to_numeric(result[value_col], errors="coerce")
    valid_values = numeric_values.dropna()

    if valid_values.empty:
        result[output_col] = pd.Series([0.0] * len(result), index=result.index, dtype="Float64")
        return result

    q1 = float(valid_values.quantile(0.25))
    q3 = float(valid_values.quantile(0.75))
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    capped_values = [
        0.0 if pd.isna(value) else float(min(max(float(value), lower_bound), upper_bound))
        for value in numeric_values
    ]
    result[output_col] = pd.Series(capped_values, index=result.index, dtype="Float64")
    return result
