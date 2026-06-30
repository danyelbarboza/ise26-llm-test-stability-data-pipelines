import pytest
import pandas as pd
from ise26.targets import join_customers_orders

# ----------------------------------------------------------------------
# Helper to assert dataframes equal ignoring index
# ----------------------------------------------------------------------
def assert_frame_equal_ignore_index(df1, df2):
    pd.testing.assert_frame_equal(df1.reset_index(drop=True), df2.reset_index(drop=True))

# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------
@pytest.fixture
def customers():
    return pd.DataFrame({
        "customer_id": [1, 2, 3, None, 5],
        "name": ["Alice", "Bob", "Charlie", "David", "Eve"],
        "email": ["alice@example.com", None, "charlie@example.com", "david@example.com", "eve@example.com"],
    })

@pytest.fixture
def orders():
    return pd.DataFrame({
        "customer_id": [1, 2, None, 4, 6],
        "order_amount": [100, 200, 300, 400, 500],
        "order_date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"],
    })

# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------
class TestJoinCustomersOrders:
    def test_basic_full_outer_join(self, customers, orders):
        """Test full outer join with matched and unmatched rows."""
        result = join_customers_orders(customers, orders, customer_key="customer_id")
        
        # Check that all rows from both sides are present
        # customers: 5 rows, orders: 5 rows, but 2 matched => 3 + 3 + 2? Let's compute
        # matched on customer_id=1 and 2 => 2 matched rows
        # customers without order: customer_id=3,5 and null => 3 rows (customer_without_order)
        # orders without customer: customer_id=4,6 and null => 3 rows (order_without_customer)
        # total = 8 rows
        assert len(result) == 8, f"Expected 8 rows, got {len(result)}"
        
        # Check record_status values
        matched = result[result["record_status"] == "matched"]
        assert len(matched) == 2, "Expected 2 matched rows"
        cust_only = result[result["record_status"] == "customer_without_order"]
        assert len(cust_only) == 3, "Expected 3 customer_without_order rows"
        order_only = result[result["record_status"] == "order_without_customer"]
        assert len(order_only) == 3, "Expected 3 order_without_customer rows"
        
        # Check that null key rows are never matched
        null_key_rows = result[result["customer_id"].isna()]
        for _, row in null_key_rows.iterrows():
            assert row["record_status"] != "matched", "Null key row should not be matched"
        
        # Check that matching rows have correct data
        row_12 = matched[matched["customer_id"] == 1]
        assert len(row_12) == 1
        assert row_12.iloc[0]["name"] == "Alice"
        assert row_12.iloc[0]["order_amount"] == 100

    def test_all_matched(self):
        """Test when every customer has an order and every order has a customer."""
        customers = pd.DataFrame({"customer_id": [1, 2], "name": ["A", "B"]})
        orders = pd.DataFrame({"customer_id": [1, 2], "amount": [10, 20]})
        result = join_customers_orders(customers, orders)
        assert len(result) == 2
        assert (result["record_status"] == "matched").all()

    def test_all_customers_unmatched(self):
        """Test when no orders exist for any customer."""
        customers = pd.DataFrame({"customer_id": [1, 2], "name": ["A", "B"]})
        orders = pd.DataFrame({"customer_id": [3, 4], "amount": [10, 20]})  # different keys
        result = join_customers_orders(customers, orders, customer_key="customer_id")
        assert len(result) == 4
        assert (result["record_status"].value_counts() == {"customer_without_order": 2, "order_without_customer": 2}).all()

    def test_all_orders_unmatched(self):
        """Test when no customers exist for any order."""
        customers = pd.DataFrame({"customer_id": [3, 4], "name": ["A", "B"]})
        orders = pd.DataFrame({"customer_id": [1, 2], "amount": [10, 20]})
        result = join_customers_orders(customers, orders)
        assert len(result) == 4
        assert (result["record_status"].value_counts() == {"customer_without_order": 2, "order_without_customer": 2}).all()

    def test_empty_dataframes(self):
        """Test with both DataFrames empty."""
        customers = pd.DataFrame({"customer_id": pd.Series(dtype="int64")})
        orders = pd.DataFrame({"customer_id": pd.Series(dtype="int64")})
        result = join_customers_orders(customers, orders)
        assert len(result) == 0

    def test_empty_customers(self, orders):
        """Test with empty customers."""
        customers = pd.DataFrame(columns=["customer_id", "name"])
        result = join_customers_orders(customers, orders)
        # orders have 5 rows, all unmatched => 5 rows
        assert len(result) == 5
        assert (result["record_status"] == "order_without_customer").all()

    def test_empty_orders(self, customers):
        """Test with empty orders."""
        orders = pd.DataFrame(columns=["customer_id", "order_amount"])
        result = join_customers_orders(customers, orders)
        assert len(result) == 5
        assert (result["record_status"] == "customer_without_order").all()

    def test_null_keys_handling(self):
        """Test that rows with null keys are handled correctly."""
        customers = pd.DataFrame({"customer_id": [None, 1], "name": ["NullCustomer", "Valid"]})
        orders = pd.DataFrame({"customer_id": [None, 1], "amount": [100, 200]})
        result = join_customers_orders(customers, orders)
        # null customer and null order: two null rows, each gets own status
        # customer_id=1 matched
        assert len(result) == 3
        for _, row in result.iterrows():
            if pd.isna(row["customer_id"]):
                if row["record_status"] == "customer_without_order":
                    assert row["name"] == "NullCustomer"
                elif row["record_status"] == "order_without_customer":
                    assert row["amount"] == 100
                else:
                    pytest.fail(f"Unexpected status for null key: {row['record_status']}")
            else:
                assert row["record_status"] == "matched"
                assert row["name"] == "Valid"
                assert row["amount"] == 200

    def test_duplicate_keys(self):
        """Test behavior when duplicate keys exist (multiple orders per customer)."""
        customers = pd.DataFrame({"customer_id": [1, 2], "name": ["A", "B"]})
        orders = pd.DataFrame({"customer_id": [1, 1, 2], "amount": [10, 20, 30]})
        result = join_customers_orders(customers, orders)
        # customer 1 matched twice, customer 2 matched once
        assert len(result) == 3
        assert (result["record_status"] == "matched").all()
        # order columns duplicated ?
        # First order with amount=10, second amount=20
        amounts = result[result["customer_id"] == 1]["amount"].tolist()
        assert 10 in amounts
        assert 20 in amounts

    def test_additional_columns_missing(self):
        """Test when one side has columns not present in the other."""
        customers = pd.DataFrame({"customer_id": [1], "name": ["Alice"], "extra_cust": ["X"]})
        orders = pd.DataFrame({"customer_id": [2], "order_amount": [100], "extra_order": ["Y"]})
        result = join_customers_orders(customers, orders)
        assert len(result) == 2
        # customer without order should have extra_order as NaN
        cust_row = result[result["record_status"] == "customer_without_order"].iloc[0]
        assert pd.isna(cust_row["extra_order"])
        # order without customer should have extra_cust as NaN
        order_row = result[result["record_status"] == "order_without_customer"].iloc[0]
        assert pd.isna(order_row["extra_cust"])

    def test_original_dataframes_unchanged(self, customers, orders):
        """Test that the input DataFrames are not mutated."""
        cust_copy = customers.copy()
        ord_copy = orders.copy()
        _ = join_customers_orders(customers, orders)
        assert customers.equals(cust_copy), "Customers DataFrame was modified"
        assert orders.equals(ord_copy), "Orders DataFrame was modified"

    def test_deterministic_sort(self):
        """Test that the output is sorted deterministically based on source order and status."""
        customers = pd.DataFrame({"customer_id": [3, 1, 2], "name": ["C", "A", "B"]})
        orders = pd.DataFrame({"customer_id": [2, 1], "amount": [20, 10]})
        result1 = join_customers_orders(customers, orders)
        result2 = join_customers_orders(customers, orders)
        assert_frame_equal_ignore_index(result1, result2)

    def test_index_reset(self):
        """Test that the result has a default integer index (0,1,2,...)."""
        customers = pd.DataFrame({"customer_id": [1, 2]})
        orders = pd.DataFrame({"customer_id": [1]})
        result = join_customers_orders(customers, orders)
        assert list(result.index) == list(range(len(result)))

    def test_custom_customer_key(self):
        """Test with a different key column name."""
        customers = pd.DataFrame({"key": [1, 2], "name": ["A", "B"]})
        orders = pd.DataFrame({"key": [1, 3], "amount": [10, 30]})
        result = join_customers_orders(customers, orders, customer_key="key")
        assert len(result) == 3
        # matched: key=1, customer_without_order: key=2, order_without_customer: key=3
        statuses = result.set_index("key")["record_status"].to_dict()
        assert statuses[1] == "matched"
        assert statuses[2] == "customer_without_order"
        assert statuses[3] == "order_without_customer"