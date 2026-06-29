"""Buggy variant for F02 that keeps the first duplicate."""

from __future__ import annotations

import pandas as pd

from ..correct import *  # noqa: F401,F403


def deduplicate_events(
    df: pd.DataFrame,
    id_col: str = "event_id",
    timestamp_col: str = "updated_at",
) -> pd.DataFrame:
    """Return a buggy deduplication result that keeps the first row.

    This version preserves rows with null identifiers but retains the first
    duplicate encountered for each event identifier instead of the most recent
    one.

    Args:
        df: Source DataFrame with event records.
        id_col: Column that identifies an event entity.
        timestamp_col: Column containing the update timestamp.

    Returns:
        A new DataFrame with buggy duplicate handling.
    """

    # BUG: The first duplicate is retained instead of the most recent row.
    result = df.copy(deep=True)
    identified_rows = result[result[id_col].notna()].drop_duplicates(subset=[id_col], keep="first")
    unidentified_rows = result[result[id_col].isna()]
    return pd.concat([identified_rows, unidentified_rows], ignore_index=True)
