"""Buggy variant for F01 that mishandles null customer names."""

from __future__ import annotations

import unicodedata

import pandas as pd

from ..correct import *  # noqa: F401,F403


def clean_customer_names(
    df: pd.DataFrame,
    name_col: str = "customer_name",
    output_col: str = "customer_name_clean",
) -> pd.DataFrame:
    """Return a buggy name-normalization result that does not treat nulls.

    This version converts null values to strings such as ``"none"`` or
    ``"nan"`` instead of preserving them as missing values.

    Args:
        df: Source DataFrame containing raw customer names.
        name_col: Column that stores the raw customer name.
        output_col: Name of the normalized output column.

    Returns:
        A new DataFrame with a buggy normalized name column.
    """

    # BUG: Null values are converted to text instead of becoming pd.NA.
    result = df.copy(deep=True)
    normalized = result[name_col].apply(
        lambda value: "missing"
        if pd.isna(value)
        else "".join(
            char
            for char in unicodedata.normalize(
                "NFKD",
                " ".join(str(value).split()).strip().lower(),
            )
            if not unicodedata.combining(char)
        )
    )
    result[output_col] = normalized
    return result
