"""Buggy variant for F10 that fails to strip the R$ prefix cleanly."""

from __future__ import annotations

import pandas as pd

from ..correct import *  # noqa: F401,F403


def standardize_currency_values(
    df: pd.DataFrame,
    value_col: str = "amount_raw",
    output_col: str = "amount",
) -> pd.DataFrame:
    """Return a buggy currency parser that leaves the currency prefix intact."""

    # BUG: The R$ prefix is not removed before parsing the numeric text.
    result = df.copy(deep=True)
    parsed_values: list[object] = []

    for value in result[value_col]:
        if pd.isna(value):
            parsed_values.append(pd.NA)
            continue

        text = str(value).strip()
        if text == "":
            parsed_values.append(pd.NA)
            continue

        try:
            parsed_values.append(float(text))
        except ValueError:
            parsed_values.append(pd.NA)

    result[output_col] = pd.Series(parsed_values, index=result.index, dtype="Float64")
    return result
