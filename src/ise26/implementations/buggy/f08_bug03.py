"""Buggy variant for F08 that computes row-level rates before grouping."""

from __future__ import annotations

import pandas as pd

from ..correct import *  # noqa: F401,F403


def calculate_conversion_rate(
    df: pd.DataFrame,
    group_col: str = "channel",
    visits_col: str = "visits",
    conversions_col: str = "conversions",
) -> pd.DataFrame:
    """Return a buggy conversion summary that averages row-level rates."""

    # BUG: The rate is computed per row before aggregation, which changes the final metric.
    result = df.copy(deep=True)
    result["_visits"] = pd.to_numeric(result[visits_col], errors="coerce").fillna(0)
    result["_conversions"] = pd.to_numeric(result[conversions_col], errors="coerce").fillna(0)
    result["_row_rate"] = result.apply(
        lambda row: 0.0 if row["_visits"] <= 0 else float(row["_conversions"] / row["_visits"]),
        axis=1,
    )

    grouped = (
        result.groupby(group_col, as_index=False, dropna=False)[["_visits", "_conversions", "_row_rate"]]
        .mean()
        .sort_values(group_col, kind="stable")
        .reset_index(drop=True)
    )

    grouped["visits"] = grouped["_visits"].astype(float)
    grouped["conversions"] = grouped["_conversions"].astype(float)
    grouped["conversion_rate"] = grouped["_row_rate"].astype(float)

    return grouped[[group_col, "visits", "conversions", "conversion_rate"]]
