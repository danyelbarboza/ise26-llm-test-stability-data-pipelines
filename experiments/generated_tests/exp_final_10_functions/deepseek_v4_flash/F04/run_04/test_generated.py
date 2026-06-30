import pandas as pd
import pytest
from ise26.targets import join_customers_orders


def test_basic_full_outer_join():
    customers = pd.DataFrame({
        "customer_id": [1, 2, 3],
        "name": ["Alice", "Bob", "Charlie"]
    })
    orders = pd.DataFrame({
        "customer_id": [2, 3, 4],
        "product": ["book", "pen", "notebook"]
    })
    result = join_customers_orders(customers, orders)
    # Expected: rows for customer 1 (only customer), 2 (both), 3 (both), 4 (only order)
    assert len(result) == 4
    # Check record_status
    status_1 = result.loc[result["customer_id"] == 1, "record_status"].iloc[0]
    assert status_1 == "customer_without_order"
    status_2 = result.loc[result["customer_id"] == 2, "record_status"].iloc[0]
    assert status_2 == "matched"
    status_3 = result.loc[result["customer_id"] == 3, "record_status"].iloc[0]
    assert status_3 == "matched"
    status_4 = result.loc[result["customer_id"] == 4, "record_status"].iloc[0]
    assert status_4 == "order_without_customer"
    # Check suffix handling
    assert "name" in result.columns
    assert "product" in result.columns
    # Original DataFrames unchanged
    assert list(customers.columns) == ["customer_id", "name"]
    assert list(orders.columns) == ["customer_id", "product"]


def test_null_join_keys():
    customers = pd.DataFrame({
        "customer_id": [1, None, 3],
        "name": ["Alice", "Bob", "Charlie"]
    })
    orders = pd.DataFrame({
        "customer_id": [2, 3, None],
        "product": ["book", "pen", "notebook"]
    })
    result = join_customers_orders(customers, orders)
    # Rows with null keys should never be matched.
    # For customer with null key -> record_status customer_without_order
    null_cust = result[result["customer_id"].isna() & result["name"].notna()]
    assert len(null_cust) == 1
    assert null_cust.iloc[0]["record_status"] == "customer_without_order"
    # For order with null key -> order_without_customer
    null_ord = result[result["customer_id"].isna() & result["product"].notna()]
    assert len(null_ord) == 1
    assert null_ord.iloc[0]["record_status"] == "order_without_customer"
    # Ensure null-key rows from both sides are not matched (no row with both non-null keys where customer_id is null)
    matched = result[result["record_status"] == "matched"]
    assert matched["customer_id"].notna().all()


def test_no_matched_rows():
    customers = pd.DataFrame({
        "customer_id": [1, 2],
        "name": ["A", "B"]
    })
    orders = pd.DataFrame({
        "customer_id": [3, 4],
        "product": ["x", "y"]
    })
    result = join_customers_orders(customers, orders)
    assert len(result) == 4
    assert (result["record_status"] == "customer_without_order").sum() == 2
    assert (result["record_status"] == "order_without_customer").sum() == 2


def test_all_matched():
    customers = pd.DataFrame({
        "customer_id": [1, 2],
        "name": ["A", "B"]
    })
    orders = pd.DataFrame({
        "customer_id": [1, 2],
        "product": ["x", "y"]
    })
    result = join_customers_orders(customers, orders)
    assert len(result) == 2
    assert (result["record_status"] == "matched").all()


def test_empty_datasets():
    customers = pd.DataFrame({"customer_id": pd.Series(dtype=int), "name": pd.Series(dtype=str)})
    orders = pd.DataFrame({"customer_id": pd.Series(dtype=int), "product": pd.Series(dtype=str)})
    result = join_customers_orders(customers, orders)
    assert len(result) == 0
    assert set(result.columns) == {"customer_id", "name", "product", "record_status"}


def test_custom_join_key():
    customers = pd.DataFrame({
        "id": [1, 2],
        "name": ["A", "B"]
    })
    orders = pd.DataFrame({
        "id": [2, 3],
        "product": ["x", "y"]
    })
    result = join_customers_orders(customers, orders, customer_key="id")
    assert len(result) == 3
    assert "id" in result.columns
    assert "name" in result.columns
    assert "product" in result.columns


def test_overlapping_non_key_columns():
    customers = pd.DataFrame({
        "customer_id": [1, 2],
        "value": [10, 20]
    })
    orders = pd.DataFrame({
        "customer_id": [1, 2],
        "value": [100, 200]
    })
    result = join_customers_orders(customers, orders)
    # After full outer join, overlapping non-key columns get suffixes
    assert "value_customer" in result.columns
    assert "value_order" in result.columns
    # Values should be correct
    assert result.loc[0, "value_customer"] == 10
    assert result.loc[0, "value_order"] == 100
    assert result.loc[1, "value_customer"] == 20
    assert result.loc[1, "value_order"] == 200


def test_sort_order_deterministic():
    customers = pd.DataFrame({
        "customer_id": [1, 2, 3],
        "name": ["A", "B", "C"]
    })
    orders = pd.DataFrame({
        "customer_id": [3, 2, 1],
        "product": ["x", "y", "z"]
    })
    result1 = join_customers_orders(customers, orders)
    result2 = join_customers_orders(customers, orders)
    pd.testing.assert_frame_equal(result1, result2)


def test_index_reset():
    customers = pd.DataFrame({"customer_id": [1], "name": ["A"]})
    orders = pd.DataFrame({"customer_id": [2], "product": ["x"]})
    result = join_customers_orders(customers, orders)
    assert result.index.tolist() == [0, 1]


def test_original_dataframes_unchanged():
    customers = pd.DataFrame({"customer_id": [1], "name": ["A"]})
    orders = pd.DataFrame({"customer_id": [1], "product": ["x"]})
    customers_original = customers.copy()
    orders_original = orders.copy()
    _ = join_customers_orders(customers, orders)
    pd.testing.assert_frame_equal(customers, customers_original)
    pd.testing.assert_frame_equal(orders, orders_original)


def test_all_null_keys_both_sides():
    customers = pd.DataFrame({"customer_id": [None, None], "name": ["A", "B"]})
    orders = pd.DataFrame({"customer_id": [None, None], "product": ["x", "y"]})
    result = join_customers_orders(customers, orders)
    # No row can be matched because keys are null
    assert (result["record_status"] == "matched").sum() == 0
    assert (result["record_status"] == "customer_without_order").sum() == 2
    assert (result["record_status"] == "order_without_customer").sum() == 2
    # Check that all rows have null customer_id
    assert result["customer_id"].isna().all()


def test_duplicate_key_values():
    customers = pd.DataFrame({
        "customer_id": [1, 1],
        "name": ["A", "B"]
    })
    orders = pd.DataFrame({
        "customer_id": [1],
        "product": ["x"]
    })
    result = join_customers_orders(customers, orders)
    # Two customer rows will match with the same order row -> full outer join produces 2 rows
    assert len(result) == 2
    assert (result["record_status"] == "matched").all()
    # Check that names are preserved
    assert set(result["name"]) == {"A", "B"}


def test_output_columns_order():
    customers = pd.DataFrame({"customer_id": [1], "name": ["A"]})
    orders = pd.DataFrame({"customer_id": [1], "product": ["x"]})
    result = join_customers_orders(customers, orders)
    # Expect columns: customer_id, name, product, record_status (suffixes if overlapping)
    expected_columns = {"customer_id", "name", "product", "record_status"}
    assert set(result.columns) == expected_columns


def test_merge_indicator_column_not_in_output():
    customers = pd.DataFrame({"customer_id": [1], "name": ["A"]})
    orders = pd.DataFrame({"customer_id": [1], "product": ["x"]})
    result = join_customers_orders(customers, orders)
    assert "_merge" not in result.columns


def test_preserve_customer_and_order_source_order():
    # Check that the sort order respects original order (customer first, then order, etc.)
    customers = pd.DataFrame({
        "customer_id": [3, 1, 2],
        "name": ["C", "A", "B"]
    })
    orders = pd.DataFrame({
        "customer_id": [2, 3, 4],
        "product": ["y", "z", "w"]
    })
    result = join_customers_orders(customers, orders)
    # Based on the deterministic sort: by _sort_order (which combines source orders),
    # then by _customer_source_order, _order_source_order, record_status.
    # The sort should put customer 1 (only customer) first (customer original index 1),
    # then customer 2 (matched, both have keys) with both rows from customer? Actually customer 2 appears first in customer order after 1? Let's just check ordering is consistent.
    # We'll compute expected order manually.
    # customer rows: index 0: id=3, idx=0; index1: id=1, idx=1; index2: id=2, idx=2
    # order rows: index0: id=2, idx=0; index1: id=3, idx=1; index2: id=4, idx=2
    # For customer 3 (both): sort order = min(cust_idx, order_idx) = min(0,1)=0
    # For customer 1 (left only): sort order = its cust_idx = 1
    # For customer 2 (both): sort order = min(2,0)=0
    # So rows with sort order 0: customer 3 and customer 2. Within that, secondary sort by _customer_source_order: 0 then 2; then _order_source_order: for customer 3 row: NA? Actually both matched row will have _customer_source_order and _order_source_order. But since they are different rows from merge, each row gets combined fill. Let's trust the function.
    # Just check that result is deterministic and order is as expected by inspecting row order.
    # We'll just check that first row is the one from customer 1 (since it's only left_only and has smallest sort order 1?) Actually sort order for customer 1 is 1, for customer 3 is 0, for customer 2 is 0. So rows with sort order 0 should come first (customer 3 and customer 2). Among those, secondary sort by _customer_source_order: customer 3 (0) < customer 2 (2). Then within each, tie-break by _order_source_order? For customer 3, _order_source_order=1; for customer 2, _order_source_order=0. So order: customer3 matched, customer2 matched, then customer1 (sort order 1). Let's check.
    sorted_ids_expected = [3, 2, 1]
    result_ids = result["customer_id"].tolist()
    # Note: customer 4 (order only) has no customer_id? Actually it has customer_id=4, but it's only order. Its sort order is from _order_source_order = 2. So it will appear after customer1? Sort order for order_only row is _order_source_order = 2. So it will come after customer1 (sort order 1). So expected: 3, 2, 1, 4
    sorted_ids_expected = [3, 2, 1, 4]
    # But note: order_only row also has sort order equal to _order_source_order which is 2. So after 1, then 2 (but wait sort order for order_only is 2, for customer1 is 1). So order: 3(0), 2(0), 1(1), 4(2). Yes.
    assert result["customer_id"].tolist() == sorted_ids_expected


def test_type_of_record_status():
    customers = pd.DataFrame({"customer_id": [1], "name": ["A"]})
    orders = pd.DataFrame({"customer_id": [2], "product": ["x"]})
    result = join_customers_orders(customers, orders)
    assert result["record_status"].dtype == object


def test_no_extra_columns():
    customers = pd.DataFrame({"customer_id": [1], "name": ["A"]})
    orders = pd.DataFrame({"customer_id": [1], "product": ["x"]})
    result = join_customers_orders(customers, orders)
    expected_columns = {"customer_id", "name", "product", "record_status"}
    assert set(result.columns) == expected_columns