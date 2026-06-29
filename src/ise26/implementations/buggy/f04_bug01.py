"""Buggy variant for F04 that uses an inner join."""

from __future__ import annotations

import pandas as pd

from ..correct import *  # noqa: F401,F403


def join_customers_orders(
    customers: pd.DataFrame,
    orders: pd.DataFrame,
    customer_key: str = "customer_id",
) -> pd.DataFrame:
    """Return a buggy join result that drops unmatched rows.

    This version joins customers and orders using an inner join, which means
    rows without a counterpart are lost.

    Args:
        customers: Customer DataFrame.
        orders: Order DataFrame.
        customer_key: Join key shared by both datasets.

    Returns:
        A DataFrame with buggy join behavior.
    """

    # BUG: Uses an inner join instead of a full outer join.
    merged = customers.copy(deep=True).merge(
        orders.copy(deep=True),
        on=customer_key,
        how="inner",
        indicator=True,
    )
    merged["record_status"] = "matched"
    return merged.drop(columns="_merge")
