"""Buggy variant for F10 that parses Brazilian separators incorrectly."""

from __future__ import annotations

import re

import pandas as pd

from ..correct import *  # noqa: F401,F403


def standardize_currency_values(
    df: pd.DataFrame,
    value_col: str = "amount_raw",
    output_col: str = "amount",
) -> pd.DataFrame:
    """Return a buggy currency parser that mishandles Brazilian separators."""

    # BUG: Brazilian-style values keep the decimal comma in the wrong position.
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

        cleaned_text = re.sub(r"[^0-9,.\-]", "", text)
        cleaned_text = cleaned_text.replace(",", "")
        try:
            parsed_values.append(float(cleaned_text))
        except ValueError:
            parsed_values.append(pd.NA)

    result[output_col] = pd.Series(parsed_values, index=result.index, dtype="Float64")
    return result
