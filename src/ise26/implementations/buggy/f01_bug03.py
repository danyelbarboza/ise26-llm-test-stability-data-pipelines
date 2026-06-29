"""Buggy variant for F01 that keeps extra internal spaces."""

from __future__ import annotations

import unicodedata

import pandas as pd

from ..correct import *  # noqa: F401,F403


def clean_customer_names(
    df: pd.DataFrame,
    name_col: str = "customer_name",
    output_col: str = "customer_name_clean",
) -> pd.DataFrame:
    """Return a buggy name-normalization result that keeps extra spaces.

    This version lowercases and removes accents, but it only trims leading and
    trailing whitespace instead of collapsing repeated internal whitespace.

    Args:
        df: Source DataFrame containing raw customer names.
        name_col: Column that stores the raw customer name.
        output_col: Name of the normalized output column.

    Returns:
        A new DataFrame with a buggy normalized name column.
    """

    # BUG: Repeated internal spaces are not collapsed.
    result = df.copy(deep=True)

    def normalize_value(value: object) -> object:
        """Normalize a value while intentionally preserving extra spaces."""

        if pd.isna(value):
            return pd.NA

        stripped = str(value).strip().lower()
        if stripped == "":
            return pd.NA

        return "".join(
            char for char in unicodedata.normalize("NFKD", stripped) if not unicodedata.combining(char)
        )

    result[output_col] = result[name_col].apply(normalize_value)
    return result
