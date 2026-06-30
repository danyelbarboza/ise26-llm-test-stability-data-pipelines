"""Buggy variant for F08 that reverses the conversion-rate formula."""

from __future__ import annotations

import pandas as pd

from ..correct import *  # noqa: F401,F403


def calculate_conversion_rate(
    df: pd.DataFrame,
    group_col: str = "channel",
    visits_col: str = "visits",
    conversions_col: str = "conversions",
) -> pd.DataFrame:
    """Return a buggy conversion summary that divides visits by conversions."""

    # BUG: The rate uses visits divided by conversions instead of conversions divided by visits.
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
    grouped["conversion_rate"] = grouped.apply(
        lambda row: 0.0 if row["conversions"] <= 0 else float(row["visits"] / row["conversions"]),
        axis=1,
    )

    return grouped[[group_col, "visits", "conversions", "conversion_rate"]]
