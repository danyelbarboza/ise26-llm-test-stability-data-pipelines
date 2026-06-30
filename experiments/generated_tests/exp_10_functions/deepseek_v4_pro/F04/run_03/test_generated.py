import pandas as pd
import pytest
from ise26.targets import join_customers_orders


def sample_customers():
    return pd.DataFrame({
        "customer_id": [1, 2, 3, None, 5, 5],
        "name": ["Alice", "Bob", "Charlie", "Diana", "Eve", "Eve Duplicate"],
        "region": ["NA", "EMEA", "APAC", "LATAM", "NA", "NA"],
    })


def sample_orders():
    return pd.DataFrame({
        "customer_id": [1, 2, 5, None, 5],
        "order_id": [101, 102, 103, 104, 105],
        "amount": [250.0, 150.0, 300.0, 120.0, 50.0],
    })


def test_basic_full_outer_join():
    customers = sample_customers()
    orders = sample_orders()
    result = join_customers_orders(customers, orders)

    # Check required columns: all customer columns + all order columns + record_status
    expected_cols = {"customer_id", "name", "region", "order_id", "amount", "record_status"}
    assert set(result.columns) == expected_cols

    # Check status counts
    status_counts = result["record_status"].value_counts()
    # 1 matched (customer_id=1), 1 matched (2), 2 matched (5 with two customers and two orders? Actually order 103 and 105 match Eve and Eve Duplicate)
    # but careful: customers has two rows with id=5 (Eve, Eve Duplicate). orders has two rows with id=5 (order 103 and 105). merge will produce 2x2 = 4 rows with both, status 'matched'
    # then we also have unmatched: customer 3 (Charlie) -> left_only, orders None (customer_without_order)
    # order with id None? Actually order 104 has customer_id=None, that will be handled as null key and not matched, status order_without_customer
    # So matched count: id 1 (1), id 2 (1), id 5 (4) = 6
    assert status_counts["matched"] == 6
    assert status_counts["customer_without_order"] == 1  # Charlie
    assert status_counts["order_without_customer"] == 0  # order 104? It has null key, so it's handled as null-key order, status order_without_customer. Wait that would be 1.
    # Actually: order 104 has customer_id=None, that is a null key. The function groups null-key rows separately, they get status order_without_customer. So record_status of order_without_customer should be 1.
    # Check: orders sample has order_id=104 with None. That row gets order_without_customer. So count=1.
    # But earlier status_counts? Let's recalc.
    # Let's simulate: customers has None -> Diana, status customer_without_order. That's 1. orders has None -> order 104, status order_without_customer. That's 1. So total customer_without_order = 1 (Charlie) + 1 (Diana) = 2, order_without_customer = 1.
    # Hmm: Diana also has customer_id=None, so she's in null-key rows and gets customer_without_order. That makes 2 customer_without_order.
    # The test above said customer_without_order=1 which is wrong if we had Diana. Well sample_customers has row 3 with None (Diana). So customer_without_order = 2.
    # Let's correct: customers has rows 0-5. customer_id: 1,2,3,None,5,5. Null key row is Diana (index 3). So she is customer_without_order. And id=3 Charlie has no matching order (orders have 1,2,5,None,5) so he is left_only -> customer_without_order. So total customer_without_order = 2.
    # order_without_customer: order 104 (None) is null key, status order_without_customer = 1.
    # So assert accordingly.

    # I'll rewrite this test to compute expected statuses.

    expected_status = {
        "matched": 6,  # (1,1) -> 1, (2,2) -> 1, (5,5) -> 4 rows
        "customer_without_order": 2,  # Charlie (id=3, non-null but no order), Diana (null key)
        "order_without_customer": 1,  # order 104 (null key)
    }
    for status, cnt in expected_status.items():
        assert status_counts.get(status, 0) == cnt, f"Expected {cnt} rows with {status}"

    # Verify that original dfs unchanged
    original_customers = sample_customers()
    original_orders = sample_orders()
    pd.testing.assert_frame_equal(customers, original_customers)
    pd.testing.assert_frame_equal(orders, original_orders)

    # Index should be reset
    assert result.index.equals(pd.RangeIndex(len(result)))


def test_null_keys_explicitly_not_matched():
    customers = pd.DataFrame({
        "customer_id": [None, None, 1],
        "name": ["A", "B", "C"],
    })
    orders = pd.DataFrame({
        "customer_id": [None, 1],
        "order_id": [100, 200],
    })
    result = join_customers_orders(customers, orders)

    # All null-key rows from customers -> customer_without_order
    # The row with key 1 will match order 200 -> matched
    # Null-key rows from orders -> order_without_customer
    # So statuses: 2 customer_without_order, 1 matched, 1 order_without_customer
    status_counts = result["record_status"].value_counts()
    assert status_counts["customer_without_order"] == 2
    assert status_counts["matched"] == 1
    assert status_counts["order_without_customer"] == 1

    # No "matched" for rows with null keys
    null_in_customers = result[result["customer_id"].isna() & (result["record_status"] != "order_without_customer")]
    assert all(null_in_customers["record_status"] == "customer_without_order")

    null_in_orders = result[result["customer_id"].isna() & (result["record_status"] != "customer_without_order")]
    assert all(null_in_orders["record_status"] == "order_without_customer")


def test_duplicate_keys_multiple_combinations():
    customers = pd.DataFrame({
        "customer_id": [1, 1, 2],
        "info": ["a", "b", "c"],
    })
    orders = pd.DataFrame({
        "customer_id": [1, 1],
        "order": [10, 20],
    })
    result = join_customers_orders(customers, orders)

    # 2 customers x 2 orders with id=1 -> 4 matched rows, plus customer id=2 unmatched -> customer_without_order
    status_counts = result["record_status"].value_counts()
    assert status_counts["matched"] == 4
    assert status_counts["customer_without_order"] == 1


def test_empty_inputs():
    empty_cust = pd.DataFrame(columns=["customer_id", "name"])
    empty_ord = pd.DataFrame(columns=["customer_id", "order_id"])

    # Both empty
    result = join_customers_orders(empty_cust, empty_ord, "customer_id")
    assert len(result) == 0
    assert set(result.columns) == {"customer_id", "name", "order_id", "record_status"}

    # Customers empty, orders present
    orders = pd.DataFrame({"customer_id": [1], "order_id": [100]})
    result = join_customers_orders(empty_cust, orders, "customer_id")
    assert len(result) == 1
    assert result.loc[0, "record_status"] == "order_without_customer"

    # Orders empty, customers present
    customers = pd.DataFrame({"customer_id": [1], "name": ["X"]})
    result = join_customers_orders(customers, empty_ord, "customer_id")
    assert len(result) == 1
    assert result.loc[0, "record_status"] == "customer_without_order"


def test_original_dataframes_unchanged():
    customers = sample_customers()
    orders = sample_orders()
    cust_copy = customers.copy(deep=True)
    ord_copy = orders.copy(deep=True)

    _ = join_customers_orders(customers, orders)

    pd.testing.assert_frame_equal(customers, cust_copy)
    pd.testing.assert_frame_equal(orders, ord_copy)


def test_deterministic_sorting():
    # Use simple DataFrames with known row order
    customers = pd.DataFrame({
        "customer_id": [3, 1, 2, None],
        "name": ["third", "first", "second", "null_cust"],
    })
    orders = pd.DataFrame({
        "customer_id": [2, None, 1],
        "order_id": [200, 300, 100],
    })

    result = join_customers_orders(customers, orders)

    # Expected order logic:
    # rows from matched merge get _sort_order = _customer_source_order if available else _order_source_order
    # then sorted by _sort_order, then _customer_source_order, _order_source_order, record_status.
    # Unmatched rows from customers (null key) get _sort_order = their _customer_source_order.
    # Unmatched rows from orders (null key) get _sort_order = their _order_source_order.
    # We'll check that the result matches this manually computed order.

    # Let's build expected order manually:
    # Customers: index 0 -> id=3, _customer_source_order=0
    # index 1 -> id=1, _customer_source_order=1
    # index 2 -> id=2, _customer_source_order=2
    # index 3 -> id=None, _customer_source_order=3
    # Orders: index 0 -> id=2, _order_source_order=0
    # index 1 -> id=None, _order_source_order=1
    # index 2 -> id=1, _order_source_order=2

    # Merge non-null keys:
    # id=1: cust row (1) & order row (2) -> both -> matched, _sort_order = 1 (from _customer_source_order), _customer_source_order=1, _order_source_order=2
    # id=2: cust row (2) & order row (0) -> both -> matched, _sort_order = 2 (from _customer_source_order), _customer_source_order=2, _order_source_order=0
    # id=3: cust row (0) left only -> customer_without_order, _sort_order = 0, _customer_source_order=0, _order_source_order=NaN

    # Null key customers: cust row (3) -> customer_without_order, _sort_order = 3
    # Null key orders: order row (1) -> order_without_customer, _sort_order = 1

    # Now sort: _sort_order asc, then _customer_source_order asc, _order_source_order asc, record_status string.
    # So order:
    # 1. _sort_order=0 -> id=3 customer_without_order (customer row 0)
    # 2. _sort_order=1 -> possibility: matched (id=1) with _sort_order=1, or order_without_customer (null order) with _sort_order=1
    #    For _sort_order=1, we compare _customer_source_order: matched row has 1, order_without_customer has NaN (since customer columns are NaN). NaN goes last due to na_position="last" in sort? The sort is done after assigning _sort_order, etc. The `sort_values` uses `na_position="last"` for NaN. So for order_without_customer, _customer_source_order=NaN, _order_source_order=1 (from original order). So _customer_source_order is NaN -> last in its group. So matched row (1,2) comes before the order_without_customer row because its _customer_source_order=1 is non-NaN.
    #    So order: matched(id=1), then order_without_customer(id=None)
    # 3. _sort_order=2 -> matched(id=2) _customer_source_order=2, _order_source_order=0
    # 4. _sort_order=3 -> customer_without_order(null cust) _customer_source_order=3

    # Thus expected sequence: customer_without_order id=3, matched id=1, order_without_customer (null), matched id=2, customer_without_order (null cust).
    expected_status_seq = [
        "customer_without_order",  # id=3
        "matched",                 # id=1
        "order_without_customer",  # id=None (order 300)
        "matched",                 # id=2
        "customer_without_order",  # id=None (cust null)
    ]
    actual_status = result["record_status"].tolist()
    assert actual_status == expected_status_seq

    # Additional check: customer_id values in that order
    expected_ids = [3.0, 1.0, None, 2.0, None]  # last None is from null cust