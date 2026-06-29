"""Buggy variant for F06 that treats zero amounts as valid."""

from __future__ import annotations

from typing import Any

import pandas as pd

from ..correct import *  # noqa: F401,F403


def classify_payment_status(
    df: pd.DataFrame,
    reference_date: Any,
    due_date_col: str = "due_date",
    paid_date_col: str = "paid_date",
    amount_col: str = "amount",
    output_col: str = "payment_status",
) -> pd.DataFrame:
    """Return a buggy payment classification that allows zero amounts.

    This version only rejects negative or missing amounts, which means rows
    with a zero amount can be classified as pending or overdue.

    Args:
        df: Source DataFrame with payment information.
        reference_date: Date used to classify unpaid records.
        due_date_col: Column containing the due date.
        paid_date_col: Column containing the payment date.
        amount_col: Column containing the payment amount.
        output_col: Name of the output classification column.

    Returns:
        A new DataFrame with buggy payment statuses.
    """

    # BUG: Zero amounts are treated as valid instead of invalid.
    parsed_reference_date = pd.to_datetime(reference_date, errors="coerce")
    if pd.isna(parsed_reference_date):
        raise ValueError("reference_date must be a valid date-like value")

    result = df.copy(deep=True)
    due_dates = pd.to_datetime(result[due_date_col], errors="coerce")
    paid_dates = pd.to_datetime(result[paid_date_col], errors="coerce")
    amounts = pd.to_numeric(result[amount_col], errors="coerce")
    paid_date_text = result[paid_date_col].astype("string").str.strip()
    paid_date_provided = result[paid_date_col].notna() & paid_date_text.ne("").fillna(False)

    statuses = pd.Series(index=result.index, dtype="object")

    invalid_paid_date_mask = paid_date_provided & paid_dates.isna()
    invalid_mask = due_dates.isna() | amounts.isna() | (amounts < 0) | invalid_paid_date_mask
    statuses.loc[invalid_mask] = "invalid"

    statuses.loc[(~invalid_mask) & paid_dates.notna() & (paid_dates <= due_dates)] = "paid_on_time"
    statuses.loc[(~invalid_mask) & paid_dates.notna() & (paid_dates > due_dates)] = "paid_late"

    unpaid_mask = (~invalid_mask) & paid_dates.isna()
    statuses.loc[unpaid_mask & (parsed_reference_date > due_dates)] = "overdue"
    statuses.loc[unpaid_mask & (parsed_reference_date <= due_dates)] = "pending"

    result[output_col] = statuses
    return result
