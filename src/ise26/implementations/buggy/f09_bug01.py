"""Buggy variant for F09 that uses mean and standard deviation."""

from __future__ import annotations

import pandas as pd

from ..correct import *  # noqa: F401,F403


def cap_outliers_iqr(
    df: pd.DataFrame,
    value_col: str = "amount",
    output_col: str = "amount_capped",
) -> pd.DataFrame:
    """Return a buggy capped column based on mean and standard deviation."""

    # BUG: The capping limits are based on mean and standard deviation instead of the IQR rule.
    result = df.copy(deep=True)
    numeric_values = pd.to_numeric(result[value_col], errors="coerce")
    valid_values = numeric_values.dropna()

    if valid_values.empty:
        result[output_col] = pd.Series([pd.NA] * len(result), index=result.index, dtype="Float64")
        return result

    mean_value = float(valid_values.mean())
    std_value = float(valid_values.std(ddof=0)) if len(valid_values) > 1 else 0.0
    lower_bound = mean_value - 1.5 * std_value
    upper_bound = mean_value + 1.5 * std_value
    capped_values = [
        pd.NA
        if pd.isna(value)
        else float(min(max(float(value), lower_bound), upper_bound))
        for value in numeric_values
    ]
    result[output_col] = pd.Series(capped_values, index=result.index, dtype="Float64")
    return result
