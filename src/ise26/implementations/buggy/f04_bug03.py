"""Buggy variant for F04 that misclassifies unmatched and null-key order rows."""

from __future__ import annotations

import pandas as pd

from ..correct import *  # noqa: F401,F403


def join_customers_orders(
    customers: pd.DataFrame,
    orders: pd.DataFrame,
    customer_key: str = "customer_id",
) -> pd.DataFrame:
    """Return a buggy join result with incorrect row classification.

    This version performs a full outer join but labels unmatched order rows,
    including order rows with null keys, as ``customer_without_order`` instead
    of ``order_without_customer``.

    Args:
        customers: Customer DataFrame.
        orders: Order DataFrame.
        customer_key: Join key shared by both datasets.

    Returns:
        A DataFrame with buggy join behavior.
    """

    # BUG: Order-only and null-key order rows receive the wrong status label.
    merged = customers.copy(deep=True).merge(
        orders.copy(deep=True),
        on=customer_key,
        how="outer",
        indicator=True,
        sort=False,
    )
    status_mapping = {
        "both": "matched",
        "left_only": "customer_without_order",
        "right_only": "customer_without_order",
    }
    merged["record_status"] = merged["_merge"].map(status_mapping)
    merged.loc[merged[customer_key].isna(), "record_status"] = "customer_without_order"
    return merged.drop(columns="_merge")
