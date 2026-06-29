"""Buggy variant for F01 that keeps accent marks."""

from __future__ import annotations

import pandas as pd

from ..correct import *  # noqa: F401,F403


def clean_customer_names(
    df: pd.DataFrame,
    name_col: str = "customer_name",
    output_col: str = "customer_name_clean",
) -> pd.DataFrame:
    """Return a buggy name-normalization result that keeps accents.

    This version trims whitespace, lowercases values, and preserves missing
    values, but it does not remove accent marks.

    Args:
        df: Source DataFrame containing raw customer names.
        name_col: Column that stores the raw customer name.
        output_col: Name of the normalized output column.

    Returns:
        A new DataFrame with a buggy normalized name column.
    """

    # BUG: Accent marks are preserved instead of being removed.
    result = df.copy(deep=True)

    def normalize_value(value: object) -> object:
        """Normalize a value while intentionally keeping accents."""

        if pd.isna(value):
            return pd.NA

        normalized = " ".join(str(value).split()).strip().lower()
        return normalized if normalized else pd.NA

    result[output_col] = result[name_col].apply(normalize_value)
    return result
