"""Buggy variant for F03 that sums canceled orders."""

from __future__ import annotations

import pandas as pd

from ..correct import *  # noqa: F401,F403


def calculate_monthly_revenue(
    df: pd.DataFrame,
    date_col: str = "order_date",
    amount_col: str = "amount",
    status_col: str = "status",
) -> pd.DataFrame:
    """Return a buggy revenue aggregation that includes canceled orders.

    This version converts dates and amounts similarly to the correct version,
    but it never filters canceled orders before aggregation.

    Args:
        df: Source DataFrame with order information.
        date_col: Column containing the order date.
        amount_col: Column containing the monetary amount.
        status_col: Column containing the order status.

    Returns:
        A DataFrame with buggy monthly revenue totals.
    """

    # BUG: Canceled orders are not excluded from the revenue sum.
    result = df.copy(deep=True)
    parsed_dates = pd.to_datetime(result[date_col], errors="coerce")
    normalized_amounts = pd.to_numeric(result[amount_col], errors="coerce").fillna(0)

    filtered = pd.DataFrame(
        {
            "month": parsed_dates[parsed_dates.notna()].dt.strftime("%Y-%m"),
            "revenue": normalized_amounts[parsed_dates.notna()],
        }
    )

    return filtered.groupby("month", as_index=False)["revenue"].sum().sort_values("month").reset_index(drop=True)
