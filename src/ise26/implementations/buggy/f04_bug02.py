"""Buggy variant for F04 that omits the status column."""

from __future__ import annotations

import pandas as pd

from ..correct import *  # noqa: F401,F403


def join_customers_orders(
    customers: pd.DataFrame,
    orders: pd.DataFrame,
    customer_key: str = "customer_id",
) -> pd.DataFrame:
    """Return a buggy join result without the record_status annotation.

    This version performs the correct join shape but does not provide the
    required status column that explains the row origin.

    Args:
        customers: Customer DataFrame.
        orders: Order DataFrame.
        customer_key: Join key shared by both datasets.

    Returns:
        A DataFrame with buggy join behavior.
    """

    # BUG: The required record_status column is never created.
    return customers.copy(deep=True).merge(
        orders.copy(deep=True),
        on=customer_key,
        how="outer",
    )
