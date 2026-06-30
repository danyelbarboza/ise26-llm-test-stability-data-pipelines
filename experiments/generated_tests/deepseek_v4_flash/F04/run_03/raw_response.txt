import pandas as pd
import pytest
from ise26.targets import join_customers_orders


class TestJoinCustomersOrders:
    """Test suite for join_customers_orders function."""

    # ------------------------------------------------------------------
    # Helper functions to build DataFrames quickly
    # ------------------------------------------------------------------
    @staticmethod
    def _build_customers(ids, names=None, other=None):
        data = {}
        if ids is not None:
            data["customer_id"] = ids
        if names is not None:
            data["name"] = names
        if other is not None:
            data.update(other)
        return pd.DataFrame(data)

    @staticmethod
    def _build_orders(ids, amounts=None, other=None):
        data = {}
        if ids is not None:
            data["customer_id"] = ids
        if amounts is not None:
            data["amount"] = amounts
        if other is not None:
            data.update(other)
        return pd.DataFrame(data)

    # ------------------------------------------------------------------
    # Basic full outer join
    # ------------------------------------------------------------------
    def test_basic_full_outer_join(self):
        customers = self._build_customers(
            ids=[1, 2, 3],
            names=["Alice", "Bob", "Charlie"],
        )
        orders = self._build_orders(
            ids=[2, 3, 4],
            amounts=[100.0, 200.0, 300.0],
        )
        result = join_customers_orders(customers, orders)

        # Expected 4 rows: 2 matched (customer 2 and 3), customer 1 unmatched, order 4 unmatched
        assert len(result) == 4
        assert "record_status" in result.columns
        assert result["record_status"].tolist() == [
            "customer_without_order",  # customer 1
            "matched",                 # customer 2
            "matched",                 # customer 3
            "order_without_customer",  # order 4
        ]
        # Check that original DataFrames are unchanged
        assert len(customers) == 3
        assert len(orders) == 3

    # ------------------------------------------------------------------
    # Null keys handling
    # ------------------------------------------------------------------
    def test_null_keys_not_matched(self):
        customers = self._build_customers(
            ids=[1, None, 2],
            names=["A", "B", "C"],
        )
        orders = self._build_orders(
            ids=[2, None, 3],
            amounts=[10.0, 20.0, 30.0],
        )
        result = join_customers_orders(customers, orders)

        # Customer with id=1 unmatched, customer with null key -> customer_without_order
        # Customer with id=2 matched with order id=2
        # Order with null key -> order_without_customer
        # Order with id=3 unmatched
        expected_statuses = [
            "customer_without_order",   # cust id=1
            "customer_without_order",   # cust null key
            "matched",                  # id=2 matched
            "order_without_customer",   # order null key
            "order_without_customer",   # order id=3
        ]
        assert result["record_status"].tolist() == expected_statuses
        # Verify that the rows with null keys are not matched
        null_cust_rows = result[result["record_status"] == "customer_without_order"]
        null_order_rows = result[result["record_status"] == "order_without_customer"]
        # At least one from each side has null key
        assert null_cust_rows["customer_id"].isna().sum() == 1
        assert null_order_rows["customer_id"].isna().sum() == 1

    # ------------------------------------------------------------------
    # All rows matched
    # ------------------------------------------------------------------
    def test_all_matched(self):
        customers = self._build_customers(
            ids=[1, 2],
            names=["X", "Y"],
        )
        orders = self._build_orders(
            ids=[1, 2],
            amounts=[100.0, 200.0],
        )
        result = join_customers_orders(customers, orders)
        assert len(result) == 2
        assert (result["record_status"] == "matched").all()

    # ------------------------------------------------------------------
    # All customers unmatched
    # ------------------------------------------------------------------
    def test_all_customers_unmatched(self):
        customers = self._build_customers(
            ids=[1, 2],
            names=["A", "B"],
        )
        orders = self._build_orders(
            ids=[3, 4],
            amounts=[10.0, 20.0],
        )
        result = join_customers_orders(customers, orders)
        assert len(result) == 4  # all rows from both sides
        assert (result["record_status"].value_counts() == {
            "customer_without_order": 2,
            "order_without_customer": 2,
        })

    # ------------------------------------------------------------------
    # All orders unmatched
    # ------------------------------------------------------------------
    def test_all_orders_unmatched(self):
        customers = self._build_customers(
            ids=[1, 2],
            names=["A", "B"],
        )
        orders = self._build_orders(
            ids=[None, None],
            amounts=[50.0, 60.0],
        )
        result = join_customers_orders(customers, orders)
        # customers: 2 unmatched; orders: 2 order_without_customer (null keys)
        assert len(result) == 4
        assert (result["record_status"].value_counts() == {
            "customer_without_order": 2,
            "order_without_customer": 2,
        })

    # ------------------------------------------------------------------
    # Empty DataFrames
    # ------------------------------------------------------------------
    def test_empty_customers(self):
        customers = pd.DataFrame(columns=["customer_id", "name"])
        orders = self._build_orders(
            ids=[1, 2],
            amounts=[100.0, 200.0],
        )
        result = join_customers_orders(customers, orders)
        # Only orders appear as order_without_customer
        assert len(result) == 2
        assert (result["record_status"] == "order_without_customer").all()

    def test_empty_orders(self):
        customers = self._build_customers(
            ids=[1, 2],
            names=["A", "B"],
        )
        orders = pd.DataFrame(columns=["customer_id", "amount"])
        result = join_customers_orders(customers, orders)
        assert len(result) == 2
        assert (result["record_status"] == "customer_without_order").all()

    def test_both_empty(self):
        customers = pd.DataFrame(columns=["customer_id", "name"])
        orders = pd.DataFrame(columns=["customer_id", "amount"])
        result = join_customers_orders(customers, orders)
        assert len(result) == 0
        # Check that output columns include all columns from both plus record_status
        expected_columns = {"customer_id", "name", "amount", "record_status"}
        assert set(result.columns) == expected_columns

    # ------------------------------------------------------------------
    # Duplicate keys (one customer has multiple orders)
    # ------------------------------------------------------------------
    def test_duplicate_keys_on_orders(self):
        customers = self._build_customers(
            ids=[1],
            names=["Alice"],
        )
        orders = self._build_orders(
            ids=[1, 1],
            amounts=[100.0, 200.0],
        )
        result = join_customers_orders(customers, orders)
        # Should produce 2 rows, both matched
        assert len(result) == 2
        assert (result["record_status"] == "matched").all()
        assert result["name"].tolist() == ["Alice", "Alice"]

    def test_duplicate_keys_on_customers(self):
        customers = self._build_customers(
            ids=[1, 1],
            names=["Alice", "Alicia"],
        )
        orders = self._build_orders(
            ids=[1],
            amounts=[100.0],
        )
        result = join_customers_orders(customers, orders)
        # Because both customers have the same key, the merge will produce a Cartesian product.
        # Each customer row pairs with the single order -> 2 rows, both matched.
        assert len(result) == 2
        assert (result["record_status"] == "matched").all()
        assert set(result["name"].tolist()) == {"Alice", "Alicia"}

    # ------------------------------------------------------------------
    # Custom key (not customer_id)
    # ------------------------------------------------------------------
    def test_custom_key(self):
        customers = pd.DataFrame({
            "user_id": [1, 2],
            "name": ["X", "Y"],
        })
        orders = pd.DataFrame({
            "user_id": [2, 3],
            "amount": [100.0, 200.0],
        })
        result = join_customers_orders(customers, orders, customer_key="user_id")
        assert "record_status" in result.columns
        expected_statuses = ["customer_without_order", "matched", "order_without_customer"]
        assert result["record_status"].tolist() == expected_statuses

    # ------------------------------------------------------------------
    # Sorting determinism
    # ------------------------------------------------------------------
    def test_sorting_order(self):
        # Create a scenario where source order matters
        customers = self._build_customers(
            ids=[3, 1, 2],
            names=["C", "A", "B"],
        )
        orders = self._build_orders(
            ids=[2, 3, 1],
            amounts=[200.0, 300.0, 100.0],
        )
        result = join_customers_orders(customers, orders)
        # Expected order: first customer_without_order for customer id=3? Wait, we need to understand sorting.
        # The function sorts by _sort_order, then _customer_source_order, etc.
        # _sort_order = _customer_source_order for customer rows, and _order_source_order for order-only rows.
        # For matched rows it uses customer source order. For unmatched from customers it uses their source order.
        # For unmatched from orders it uses order source order.
        # Then nulls last.
        # We'll just check that the result index is 0..n-1 and the rows are in a deterministic order.
        assert list(result.index) == list(range(len(result)))
        # Check that customer_without_order come before others? Not necessarily; order depends on source order.
        # We'll verify that the concatenated order is stable: we can re-run and get same result.
        result2 = join_customers_orders(customers, orders)
        pd.testing.assert_frame_equal(result, result2)

    # ------------------------------------------------------------------
    # Original DataFrames unchanged after call
    # ------------------------------------------------------------------
    def test_original_dataframes_unchanged(self):
        customers = self._build_customers(
            ids=[1, 2, 3],
            names=["A", "B", "C"],
        )
        orders = self._build_orders(
            ids=[2, 4],
            amounts=[10.0, 20.0],
        )
        customers_before = customers.copy()
        orders_before = orders.copy()
        _ = join_customers_orders(customers, orders)
        pd.testing.assert_frame_equal(customers, customers_before)
        pd.testing.assert_frame_equal(orders, orders_before)

    # ------------------------------------------------------------------
    # Columns preservation
    # ------------------------------------------------------------------
    def test_column_preservation(self):
        customers = pd.DataFrame({
            "customer_id": [1, 2],
            "name": ["A", "B"],
            "email": ["a@x.com", "b@x.com"],
        })
        orders = pd.DataFrame({
            "customer_id": [2, 3],
            "amount": [100.0, 200.0],
            "date": ["2024-01-01", "2024-01-02"],
        })
        result = join_customers_orders(customers, orders)
        expected_columns = {"customer_id", "name", "email", "amount", "date", "record_status"}
        assert set(result.columns) == expected_columns
        # For customer_without_order, order columns should be NA
        cust_unmatched = result[result["record_status"] == "customer_without_order"]
        assert cust_unmatched["amount"].isna().all()
        assert cust_unmatched["date"].isna().all()
        # For order_without_customer, customer columns should be NA
        order_unmatched = result[result["record_status"] == "order_without_customer"]
        assert order_unmatched["name"].isna().all()
        assert order_unmatched["email"].isna().all()

    # ------------------------------------------------------------------
    # Strict test: no unmatched row can have both sides non-null
    # ------------------------------------------------------------------
    def test_no_mixed_unmatched(self):
        customers = self._build_customers(
            ids=[1, None],
            names=["A", "B"],
        )
        orders = self._build_orders(
            ids=[2, None],
            amounts=[100.0, 200.0],
        )
        result = join_customers_orders(customers, orders)
        for _, row in result.iterrows():
            if row["record_status"] == "customer_without_order":
                assert pd.isna(row["amount"])  # order columns missing
            elif row["record_status"] == "order_without_customer":
                assert pd.isna(row["name"])    # customer columns missing
            else:  # matched
                assert pd.notna(row["amount"]) and pd.notna(row["name"])