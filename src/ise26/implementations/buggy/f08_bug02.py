"""Buggy variant for F08 that does not protect against zero visits."""

from __future__ import annotations

import pandas as pd

from ..correct import *  # noqa: F401,F403


def calculate_conversion_rate(
    df: pd.DataFrame,
    group_col: str = "channel",
    visits_col: str = "visits",
    conversions_col: str = "conversions",
) -> pd.DataFrame:
    """Return a buggy conversion summary that can divide by zero."""

    # BUG: The conversion-rate formula is applied directly without zero-visit protection.
    result = df.copy(deep=True)
    aggregated = pd.DataFrame(
        {
            group_col: result[group_col],
            "_visits": pd.to_numeric(result[visits_col], errors="coerce").fillna(0),
            "_conversions": pd.to_numeric(result[conversions_col], errors="coerce").fillna(0),
        }
    )

    grouped = (
        aggregated.groupby(group_col, as_index=False, dropna=False)[["_visits", "_conversions"]]
        .sum()
        .sort_values(group_col, kind="stable")
        .reset_index(drop=True)
    )

    grouped["visits"] = grouped["_visits"].astype(float)
    grouped["conversions"] = grouped["_conversions"].astype(float)
    grouped["conversion_rate"] = grouped["conversions"] / grouped["visits"]

    return grouped[[group_col, "visits", "conversions", "conversion_rate"]]
