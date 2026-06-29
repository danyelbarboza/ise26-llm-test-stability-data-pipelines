"""Buggy variant for F03 that drops invalid amounts."""

from __future__ import annotations

import pandas as pd

from ..correct import *  # noqa: F401,F403


def calculate_monthly_revenue(
    df: pd.DataFrame,
    date_col: str = "order_date",
    amount_col: str = "amount",
    status_col: str = "status",
) -> pd.DataFrame:
    """Return a buggy revenue aggregation that skips invalid amounts.

    This version ignores canceled orders correctly, but rows with null or
    invalid amounts are dropped instead of being counted as zero.

    Args:
        df: Source DataFrame with order information.
        date_col: Column containing the order date.
        amount_col: Column containing the monetary amount.
        status_col: Column containing the order status.

    Returns:
        A DataFrame with buggy monthly revenue totals.
    """

    # BUG: Invalid amounts are dropped instead of being converted to zero.
    result = df.copy(deep=True)
    parsed_dates = pd.to_datetime(result[date_col], errors="coerce")
    normalized_status = result[status_col].astype(str).str.strip().str.lower()
    normalized_amounts = pd.to_numeric(result[amount_col], errors="coerce")
    cancelled_statuses = {"cancelled", "canceled", "cancelado"}

    valid_mask = parsed_dates.notna() & ~normalized_status.isin(cancelled_statuses) & normalized_amounts.notna()
    filtered = pd.DataFrame(
        {
            "month": parsed_dates[valid_mask].dt.strftime("%Y-%m"),
            "revenue": normalized_amounts[valid_mask],
        }
    )

    return filtered.groupby("month", as_index=False)["revenue"].sum().sort_values("month").reset_index(drop=True)
