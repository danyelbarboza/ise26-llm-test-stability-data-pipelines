"""Buggy variant for F10 that turns invalid currency text into zero."""

from __future__ import annotations

import re

import pandas as pd

from ..correct import *  # noqa: F401,F403


def standardize_currency_values(
    df: pd.DataFrame,
    value_col: str = "amount_raw",
    output_col: str = "amount",
) -> pd.DataFrame:
    """Return a buggy currency parser that uses zero for invalid values."""

    # BUG: Invalid currency strings become zero instead of pandas.NA.
    result = df.copy(deep=True)
    parsed_values: list[object] = []

    for value in result[value_col]:
        if pd.isna(value):
            parsed_values.append(0.0)
            continue

        text = str(value).strip()
        if text == "":
            parsed_values.append(0.0)
            continue

        cleaned_text = re.sub(r"[^0-9,.\-]", "", text)
        cleaned_text = cleaned_text.replace(",", "").replace(".", "")
        try:
            parsed_values.append(float(cleaned_text))
        except ValueError:
            parsed_values.append(0.0)

    result[output_col] = pd.Series(parsed_values, index=result.index, dtype="Float64")
    return result
