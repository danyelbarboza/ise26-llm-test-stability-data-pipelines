"""Buggy variant for F02 that compares timestamps as strings."""

from __future__ import annotations

import pandas as pd

from ..correct import *  # noqa: F401,F403


def deduplicate_events(
    df: pd.DataFrame,
    id_col: str = "event_id",
    timestamp_col: str = "updated_at",
) -> pd.DataFrame:
    """Return a buggy deduplication result based on string ordering.

    This version sorts timestamps lexicographically, which can lead to
    incorrect recency decisions when the date strings have different formats.

    Args:
        df: Source DataFrame with event records.
        id_col: Column that identifies an event entity.
        timestamp_col: Column containing the update timestamp.

    Returns:
        A new DataFrame with buggy duplicate handling.
    """

    # BUG: Timestamps are compared as raw strings instead of datetime values.
    result = df.copy(deep=True)
    result["_original_order"] = range(len(result))
    result["_timestamp_as_string"] = result[timestamp_col].astype(str)

    identified_rows = result[result[id_col].notna()].copy()
    unidentified_rows = result[result[id_col].isna()].copy()

    deduplicated = (
        identified_rows.sort_values(
            by=[id_col, "_timestamp_as_string", "_original_order"],
            ascending=[True, True, True],
            na_position="first",
        )
        .drop_duplicates(subset=[id_col], keep="last")
        .copy()
    )

    final_result = pd.concat([deduplicated, unidentified_rows], ignore_index=True)
    final_result = final_result.sort_values("_original_order").drop(
        columns=["_original_order", "_timestamp_as_string"]
    )

    return final_result.reset_index(drop=True)
