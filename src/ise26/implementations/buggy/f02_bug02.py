"""Buggy variant for F02 that drops rows with null identifiers."""

from __future__ import annotations

import pandas as pd

from ..correct import *  # noqa: F401,F403


def deduplicate_events(
    df: pd.DataFrame,
    id_col: str = "event_id",
    timestamp_col: str = "updated_at",
) -> pd.DataFrame:
    """Return a buggy deduplication result that discards null identifiers.

    This version keeps the most recent row among identified duplicates, but it
    incorrectly removes rows whose event identifier is missing.

    Args:
        df: Source DataFrame with event records.
        id_col: Column that identifies an event entity.
        timestamp_col: Column containing the update timestamp.

    Returns:
        A new DataFrame with buggy duplicate handling.
    """

    # BUG: Rows with null event identifiers are dropped entirely.
    result = df.copy(deep=True)
    result["_original_order"] = range(len(result))
    result["_parsed_timestamp"] = pd.to_datetime(result[timestamp_col], errors="coerce")

    identified_rows = result[result[id_col].notna()].copy()
    deduplicated = (
        identified_rows.sort_values(
            by=[id_col, "_parsed_timestamp", "_original_order"],
            ascending=[True, True, True],
            na_position="first",
        )
        .drop_duplicates(subset=[id_col], keep="last")
        .drop(columns=["_original_order", "_parsed_timestamp"])
    )

    return deduplicated.reset_index(drop=True)
