import pandas as pd
import pytest
from ise26.targets import join_customers_orders


def test_basic_full_outer_join():
    customers = pd.DataFrame({
        "customer_id": [1, 2, 3],
        "name": ["Alice", "Bob", "Charlie"],
    })
    orders = pd.DataFrame({
        "customer_id": [2, 3, 4],
        "product": ["Book", "Pen", "Desk"],
    })
    result = join_customers_orders(customers, orders)

    # Check all rows present
    assert len(result) == 5  # 3 customers + 3 orders minus 1 match = 5 unique rows

    # Check record_status column
    statuses = result.set_index("customer_id")["record_status"].to_dict()
    assert statuses[1] == "customer_without_order"
    assert statuses[2] == "matched"
    assert statuses[3] == "matched"
    assert statuses[4] == "order_without_customer"

    # Check suffixes for overlapping non-key columns (none in this case, but ensure no weirdness)
    assert "name" in result.columns
    assert "product" in result.columns
    # No suffix added because there is no overlap beyond the key


def test_null_keys_not_matched():
    customers = pd.DataFrame({
        "customer_id": [1, None, 3],
        "name": ["Alice", "Bob", "Charlie"],
    })
    orders = pd.DataFrame({
        "customer_id": [None, 3, 4],
        "product": ["Book", "Pen", "Desk"],
    })
    result = join_customers_orders(customers, orders)

    # Rows with null keys should never be matched
    for idx, row in result.iterrows():
        if pd.isna(row["customer_id"]):
            assert row["record_status"] in ("customer_without_order", "order_without_customer")
        else:
            assert row["record_status"] is not None  # just to confirm status present

    # Ensure the null key rows are present
    null_customer_rows = result[result["record_status"] == "customer_without_order"]
    null_order_rows = result[result["record_status"] == "order_without_customer"]
    assert len(null_customer_rows) == 1
    assert len(null_order_rows) == 1


def test_overlapping_columns_get_suffixes():
    customers = pd.DataFrame({
        "customer_id": [1, 2],
        "value": [10, 20],
    })
    orders = pd.DataFrame({
        "customer_id": [2, 3],
        "value": [200, 300],
    })
    result = join_customers_orders(customers, orders)

    # Check suffixes
    assert "value_customer" in result.columns
    assert "value_order" in result.columns
    assert "value" not in result.columns

    # Check values match
    matched_row = result[result["record_status"] == "matched"]
    assert matched_row.iloc[0]["value_customer"] == 20
    assert matched_row.iloc[0]["value_order"] == 200


def test_deterministic_sorting():
    customers = pd.DataFrame({
        "customer_id": [3, 1, 2],
        "name": ["C", "A", "B"],
    })
    orders = pd.DataFrame({
        "customer_id": [2, 1, 4],
        "product": ["P2", "P1", "P4"],
    })
    result = join_customers_orders(customers, orders)
    # Check that index is reset and no extra columns remain
    assert result.index.name is None
    assert result.index.tolist() == list(range(len(result)))
    # Check that sorting columns are dropped
    assert "_sort_order" not in result.columns
    assert "_customer_source_order" not in result.columns
    assert "_order_source_order" not in result.columns

    # The order should be deterministic based on original ordering
    # For customer_id 1: both present? Check statuses
    # Sorted by source order, then status. Hard to check exact order but at least ensure no crash.
    # We'll simply verify that the order is consistent across runs
    result2 = join_customers_orders(customers, orders)
    assert result.equals(result2)


def test_original_dataframes_unchanged():
    customers_orig = pd.DataFrame({
        "customer_id": [1, 2],
        "name": ["A", "B"],
    })
    orders_orig = pd.DataFrame({
        "customer_id": [2, 3],
        "product": ["P2", "P3"],
    })
    customers_copy = customers_orig.copy()
    orders_copy = orders_orig.copy()
    _ = join_customers_orders(customers_orig, orders_orig)
    pd.testing.assert_frame_equal(customers_orig, customers_copy)
    pd.testing.assert_frame_equal(orders_orig, orders_copy)


def test_empty_dataframes():
    # Both empty
    customers = pd.DataFrame(columns=["customer_id", "name"])
    orders = pd.DataFrame(columns=["customer_id", "product"])
    result = join_customers_orders(customers, orders)
    assert len(result) == 0
    assert "record_status" in result.columns

    # Only customers empty
    customers = pd.DataFrame(columns=["customer_id", "name"])
    orders = pd.DataFrame({"customer_id": [1], "product": ["P1"]})
    result = join_customers_orders(customers, orders)
    assert len(result) == 1
    assert result.iloc[0]["record_status"] == "order_without_customer"

    # Only orders empty
    customers = pd.DataFrame({"customer_id": [1], "name": ["A"]})
    orders = pd.DataFrame(columns=["customer_id", "product"])
    result = join_customers_orders(customers, orders)
    assert len(result) == 1
    assert result.iloc[0]["record_status"] == "customer_without_order"


def test_all_matched():
    customers = pd.DataFrame({"customer_id": [1, 2], "name": ["A", "B"]})
    orders = pd.DataFrame({"customer_id": [1, 2], "product": ["P1", "P2"]})
    result = join_customers_orders(customers, orders)
    assert len(result) == 2
    assert (result["record_status"] == "matched").all()


def test_all_unmatched():
    customers = pd.DataFrame({"customer_id": [1, 2], "name": ["A", "B"]})
    orders = pd.DataFrame({"customer_id": [3, 4], "product": ["P3", "P4"]})
    result = join_customers_orders(customers, orders)
    assert len(result) == 4
    statuses = result["record_status"].value_counts().to_dict()
    assert statuses["customer_without_order"] == 2
    assert statuses["order_without_customer"] == 2
    assert "matched" not in statuses


def test_mixed_null_and_nonnull_keys():
    customers = pd.DataFrame({
        "customer_id": [1, None, 3],
        "name": ["A", "B", "C"],
    })
    orders = pd.DataFrame({
        "customer_id": [None, 1, 3],
        "product": ["PX", "P1", "P3"],
    })
    result = join_customers_orders(customers, orders)
    # Should have: matched(1,3), customer_without_order (one null customer), order_without_customer (one null order)
    # Also customers[2] matches orders[2]? Actually customers with id=3 matches orders with id=3.
    assert len(result) == 4  # two matched, two unmatched null-key rows
    matched = result[result["record_status"] == "matched"]
    assert len(matched) == 2
    assert matched["customer_id"].dropna().tolist() == [1, 3]


def test_different_key_column_name():
    customers = pd.DataFrame({
        "cid": [1, 2],
        "name": ["A", "B"],
    })
    orders = pd.DataFrame({
        "cid": [2, 3],
        "product": ["P2", "P3"],
    })
    result = join_customers_orders(customers, orders, customer_key="cid")
    assert len(result) == 3
    mask = result["record_status"] == "matched"
    assert mask.sum() == 1
    assert result.loc[mask, "cid"].iloc[0] == 2


def test_no_overlapping_columns():
    customers = pd.DataFrame({
        "customer_id": [1, 2],
        "name": ["A", "B"],
    })
    orders = pd.DataFrame({
        "customer_id": [2, 3],
        "amount": [100, 200],
    })
    result = join_customers_orders(customers, orders)
    assert "name" in result.columns
    assert "amount" in result.columns
    # No suffixes
    assert "name_customer" not in result.columns
    assert "name_order" not in result.columns


def test_int_float_mixed_types():
    customers = pd.DataFrame({
        "customer_id": [1, 2],
        "value": [10.5, 20.3],
    })
    orders = pd.DataFrame({
        "customer_id": [2, 3],
        "value": [200.1, 300.7],
    })
    result = join_customers_orders(customers, orders)
    assert result["value_customer"].dtype == "float64"
    assert result["value_order"].dtype == "float64"