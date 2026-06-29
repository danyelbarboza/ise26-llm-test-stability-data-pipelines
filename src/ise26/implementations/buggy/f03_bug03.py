"""Buggy variant for F03 that groups revenue by day."""

from __future__ import annotations

import pandas as pd

from ..correct import *  # noqa: F401,F403


def calculate_monthly_revenue(
    df: pd.DataFrame,
    date_col: str = "order_date",
    amount_col: str = "amount",
    status_col: str = "status",
) -> pd.DataFrame:
    """Return a buggy aggregation that groups revenue by day.

    This version filters canceled rows and normalizes invalid amounts, but it
    uses the full date instead of the target month granularity.

    Args:
        df: Source DataFrame with order information.
        date_col: Column containing the order date.
        amount_col: Column containing the monetary amount.
        status_col: Column containing the order status.

    Returns:
        A DataFrame with buggy date-level revenue totals.
    """

    # BUG: Revenue is grouped by day instead of by month.
    result = df.copy(deep=True)
    parsed_dates = pd.to_datetime(result[date_col], errors="coerce")
    normalized_status = result[status_col].astype(str).str.strip().str.lower()
    normalized_amounts = pd.to_numeric(result[amount_col], errors="coerce").fillna(0)
    cancelled_statuses = {"cancelled", "canceled", "cancelado"}

    valid_mask = parsed_dates.notna() & ~normalized_status.isin(cancelled_statuses)
    filtered = pd.DataFrame(
        {
            "month": parsed_dates[valid_mask].dt.strftime("%Y-%m-%d"),
            "revenue": normalized_amounts[valid_mask],
        }
    )

    return filtered.groupby("month", as_index=False)["revenue"].sum().sort_values("month").reset_index(drop=True)
