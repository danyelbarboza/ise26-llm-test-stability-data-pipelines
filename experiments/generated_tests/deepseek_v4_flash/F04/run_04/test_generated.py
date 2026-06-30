import pytest
import pandas as pd
from ise26.targets import join_customers_orders


class TestJoinCustomersOrders:
    """Test suite for join_customers_orders function."""

    def test_basic_full_outer_join(self):
        """Basic full outer join with matched and unmatched rows."""
        customers = pd.DataFrame({
            "customer_id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"],
        })
        orders = pd.DataFrame({
            "customer_id": [1, 2, 4],
            "product": ["Book", "Pen", "Desk"],
        })
        result = join_customers_orders(customers, orders)
        # Expect 4 rows: customer 1 matched, 2 matched, 3 customer_without_order, 4 order_without_customer
        assert len(result) == 4
        assert set(result["customer_id"].tolist()) == {1, 2, 3, 4}
        # Check status labels
        assert result.loc[result["customer_id"] == 1, "record_status"].iloc[0] == "matched"
        assert result.loc[result["customer_id"] == 2, "record_status"].iloc[0] == "matched"
        assert result.loc[result["customer_id"] == 3, "record_status"].iloc[0] == "customer_without_order"
        assert result.loc[result["customer_id"] == 4, "record_status"].iloc[0] == "order_without_customer"
        # Check original DataFrames unchanged
        assert len(customers) == 3
        assert len(orders) == 3

    def test_custom_key_name(self):
        """Use a different join key name."""
        customers = pd.DataFrame({"cust_id": [10, 20], "name": ["X", "Y"]})
        orders = pd.DataFrame({"cust_id": [10, 30], "order": ["A", "B"]})
        result = join_customers_orders(customers, orders, customer_key="cust_id")
        assert len(result) == 3
        assert result["record_status"].tolist() == ["matched", "customer_without_order", "order_without_customer"]

    def test_null_keys_in_customers(self):
        """Customers with null join key should be classified as customer_without_order even if orders also have null."""
        customers = pd.DataFrame({
            "customer_id": [None, 1],
            "name": ["NullCustomer", "Alice"],
        })
        orders = pd.DataFrame({
            "customer_id": [None, 1],
            "product": ["NullOrder", "Book"],
        })
        result = join_customers_orders(customers, orders)
        # Null key rows should not be matched
        assert len(result) == 3  # null customer (unique), null order (unique), matched 1
        # The two null rows should have different statuses
        null_cust_mask = result["customer_id"].isna() & result["name"].notna()
        null_order_mask = result["customer_id"].isna() & result["product"].notna()
        assert null_cust_mask.any()
        assert null_order_mask.any()
        assert result.loc[null_cust_mask, "record_status"].iloc[0] == "customer_without_order"
        assert result.loc[null_order_mask, "record_status"].iloc[0] == "order_without_customer"

    def test_null_keys_in_orders(self):
        """Orders with null join key should be classified as order_without_customer."""
        customers = pd.DataFrame({
            "customer_id": [1, 2],
            "name": ["A", "B"],
        })
        orders = pd.DataFrame({
            "customer_id": [None, 1],
            "product": ["Null", "Book"],
        })
        result = join_customers_orders(customers, orders)
        assert len(result) == 3
        assert result["record_status"].value_counts()["order_without_customer"] == 1
        assert result["record_status"].value_counts()["customer_without_order"] == 1
        assert result["record_status"].value_counts()["matched"] == 1

    def test_all_null_keys(self):
        """All keys null: no matches, all rows preserved as unmatched."""
        customers = pd.DataFrame({"customer_id": [None, None], "name": ["A", "B"]})
        orders = pd.DataFrame({"customer_id": [None], "product": ["P"]})
        result = join_customers_orders(customers, orders)
        # 3 rows: 2 customer_without_order, 1 order_without_customer
        assert len(result) == 3
        assert (result["record_status"] == "customer_without_order").sum() == 2
        assert (result["record_status"] == "order_without_customer").sum() == 1

    def test_no_common_keys(self):
        """No overlapping keys: all rows should be unmatched."""
        customers = pd.DataFrame({"customer_id": [1, 2], "name": ["A", "B"]})
        orders = pd.DataFrame({"customer_id": [3, 4], "product": ["X", "Y"]})
        result = join_customers_orders(customers, orders)
        assert len(result) == 4
        assert (result["record_status"] == "customer_without_order").sum() == 2
        assert (result["record_status"] == "order_without_customer").sum() == 2

    def test_empty_dataframes(self):
        """Both DataFrames empty -> empty result."""
        customers = pd.DataFrame({"customer_id": pd.Series(dtype="int64")})
        orders = pd.DataFrame({"customer_id": pd.Series(dtype="int64")})
        result = join_customers_orders(customers, orders)
        assert len(result) == 0
        assert "record_status" in result.columns  # but empty

    def test_empty_customers(self):
        """Empty customers DataFrame."""
        customers = pd.DataFrame({"customer_id": pd.Series(dtype="int64"), "name": pd.Series(dtype="str")})
        orders = pd.DataFrame({"customer_id": [1], "product": ["Book"]})
        result = join_customers_orders(customers, orders)
        assert len(result) == 1
        assert result["record_status"].iloc[0] == "order_without_customer"

    def test_empty_orders(self):
        """Empty orders DataFrame."""
        customers = pd.DataFrame({"customer_id": [1], "name": ["Alice"]})
        orders = pd.DataFrame({"customer_id": pd.Series(dtype="int64"), "product": pd.Series(dtype="str")})
        result = join_customers_orders(customers, orders)
        assert len(result) == 1
        assert result["record_status"].iloc[0] == "customer_without_order"

    def test_duplicate_keys_in_customers(self):
        """Duplicate keys in customers: full outer join should preserve duplicates (no aggregation)."""
        customers = pd.DataFrame({
            "customer_id": [1, 1, 2],
            "name": ["A", "B", "C"],
        })
        orders = pd.DataFrame({
            "customer_id": [1, 3],
            "product": ["Book", "Desk"],
        })
        result = join_customers_orders(customers, orders)
        # Expect 4 rows: two matched (customer 1 x order 1 appears twice), one unmatched customer 2, one unmatched order 3
        assert len(result) == 4
        # Check both customer rows with id=1 are matched
        matched_1 = result[result["customer_id"] == 1]
        assert len(matched_1) == 2
        assert (matched_1["record_status"] == "matched").all()

    def test_duplicate_keys_in_orders(self):
        """Duplicate keys in orders."""
        customers = pd.DataFrame({
            "customer_id": [1, 2],
            "name": ["A", "B"],
        })
        orders = pd.DataFrame({
            "customer_id": [1, 1, 3],
            "product": ["Book", "Pen", "Desk"],
        })
        result = join_customers_orders(customers, orders)
        assert len(result) == 4  # two matched (1 repeated), one unmatched customer 2, one unmatched order 3
        matched_1 = result[result["customer_id"] == 1]
        assert len(matched_1) == 2
        assert (matched_1["record_status"] == "matched").all()

    def test_sort_order_deterministic(self):
        """Result should be sorted deterministically based on original line order."""
        customers = pd.DataFrame({
            "customer_id": [3, 1, 2],
            "name": ["C", "A", "B"],
        })
        orders = pd.DataFrame({
            "customer_id": [2, 3],
            "product": ["Y", "X"],
        })
        result = join_customers_orders(customers, orders)
        # Expected order: customer with source order: row 0 (id=3) -> matched, row 1 (id=1) -> unmatched, row 2 (id=2) -> matched
        # Then order without customer (none). So order of customer rows: 3, 1, 2.
        # After sorting by _sort_order, we expect customer_id order: 3, 1, 2.
        ids = result["customer_id"].dropna().tolist()
        # Because of sorting by source order and then other columns, we can check that customer rows appear in the original customer order.
        # But there are also order rows without customer (none). Let's just check that the first row is customer 3 (matched) and second is 1 (unmatched)
        assert result.iloc[0]["customer_id"] == 3
        assert result.iloc[1]["customer_id"] == 1
        assert result.iloc[2]["customer_id"] == 2

    def test_preserves_original_dataframes(self):
        """Original DataFrames should remain unmodified."""
        customers = pd.DataFrame({"customer_id": [1, 2], "name": ["A", "B"]})
        orders = pd.DataFrame({"customer_id": [1, 3], "product": ["X", "Y"]})
        customers_copy = customers.copy()
        orders_copy = orders.copy()
        _ = join_customers_orders(customers, orders)
        assert customers.equals(customers_copy)
        assert orders.equals(orders_copy)

    def test_output_has_correct_columns_and_index(self):
        """Output should have all columns from both inputs plus record_status, and reset index."""
        customers = pd.DataFrame({"customer_id": [1], "name": ["Alice"]})
        orders = pd.DataFrame({"customer_id": [1], "product": ["Book"], "price": [10]})
        result = join_customers_orders(customers, orders)
        expected_cols = ["customer_id", "name", "product", "price", "record_status"]
        assert sorted(result.columns.tolist()) == sorted(expected_cols)
        assert result.index.tolist() == list(range(len(result)))

    def test_no_extra_internal_columns(self):
        """Internal columns like _merge, _sort_order, _customer_source_order, _order_source_order should not appear."""
        customers = pd.DataFrame({"customer_id": [1], "name": ["A"]})
        orders = pd.DataFrame({"customer_id": [1], "product": ["B"]})
        result = join_customers_orders(customers, orders)
        internal = {"_merge", "_sort_order", "_customer_source_order", "_order_source_order"}
        assert internal.isdisjoint(set(result.columns))

    def test_different_dtypes_join_key(self):
        """Join key can be of different types (e.g., string)."""
        customers = pd.DataFrame({"customer_id": ["a", "b"], "name": ["A", "B"]})
        orders = pd.DataFrame({"customer_id": ["a", "c"], "product": ["X", "Y"]})
        result = join_customers_orders(customers, orders)
        assert len(result) == 3
        assert result.loc[result["customer_id"] == "a", "record_status"].iloc[0] == "matched"
        assert result.loc[result["customer_id"] == "b", "record_status"].iloc[0] == "customer_without_order"
        assert result.loc[result["customer_id"] == "c", "record_status"].iloc[0] == "order_without_customer"

    def test_nan_key_with_other_matches(self):
        """Null key rows should not prevent other rows from being matched."""
        customers = pd.DataFrame({"customer_id": [None, 1], "name": ["Null", "Alice"]})
        orders = pd.DataFrame({"customer_id": [None, 1], "product": ["Null", "Book"]})
        result = join_customers_orders(customers, orders)
        # Must have exactly 3 rows: null customer, null order, matched 1
        assert len(result) == 3
        matched = result[result["record_status"] == "matched"]
        assert len(matched) == 1
        assert matched.iloc[0]["customer_id"] == 1
        # The other two rows have null id
        null_rows = result[result["customer_id"].isna()]
        assert len(null_rows) == 2