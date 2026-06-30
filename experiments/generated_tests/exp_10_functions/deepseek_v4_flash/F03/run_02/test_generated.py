import pandas as pd
import pytest
from ise26.targets import calculate_monthly_revenue


class TestCalculateMonthlyRevenue:
    """Test suite for calculate_monthly_revenue function."""

    def test_basic_aggregation(self):
        """Normal case: multiple orders, mixed statuses, valid amounts."""
        df = pd.DataFrame({
            "order_date": ["2021-01-15", "2021-01-20", "2021-02-01", "2021-02-10", "2021-03-05"],
            "amount": [100.0, 200.0, 150.0, 300.0, 50.0],
            "status": ["delivered", "shipped", "cancelled", "completed", "canceled"],
        })
        result = calculate_monthly_revenue(df)
        expected = pd.DataFrame({
            "month": ["2021-01", "2021-02"],
            "revenue": [300.0, 150.0],  # January: 100+200=300, February: only 150, March cancelled
        })
        pd.testing.assert_frame_equal(result, expected)

    def test_brazilian_portuguese_status(self):
        """Verify that Portuguese statuses are recognized as cancelled."""
        df = pd.DataFrame({
            "order_date": ["2021-01-01", "2021-01-02"],
            "amount": [50.0, 100.0],
            "status": ["cancelado", "delivered"],
        })
        result = calculate_monthly_revenue(df)
        expected = pd.DataFrame({
            "month": ["2021-01"],
            "revenue": [100.0],
        })
        pd.testing.assert_frame_equal(result, expected)

    def test_case_and_spaces_in_status(self):
        """Status with mixed case and surrounding spaces should be ignored."""
        df = pd.DataFrame({
            "order_date": ["2021-01-01", "2021-01-01", "2021-01-01"],
            "amount": [10.0, 20.0, 30.0],
            "status": ["  Canceled  ", "CANCELLED", "cancelado "],
        })
        result = calculate_monthly_revenue(df)
        expected = pd.DataFrame({
            "month": [],
            "revenue": [],
        }).astype({"month": "object", "revenue": "float64"})
        pd.testing.assert_frame_equal(result, expected)

    def test_invalid_dates_ignored(self):
        """Rows with invalid or missing order dates should be excluded."""
        df = pd.DataFrame({
            "order_date": ["2021-01-01", "not_a_date", pd.NaT, "2021-01-03"],
            "amount": [100.0, 200.0, 300.0, 400.0],
            "status": ["completed", "shipped", "delivered", "completed"],
        })
        result = calculate_monthly_revenue(df)
        expected = pd.DataFrame({
            "month": ["2021-01", "2021-01"],
            "revenue": [100.0, 400.0],
        }).groupby("month", as_index=False)["revenue"].sum()
        # The expected aggregated: 500 for 2021-01
        expected_agg = pd.DataFrame({
            "month": ["2021-01"],
            "revenue": [500.0],
        })
        pd.testing.assert_frame_equal(result, expected_agg)

    def test_invalid_amounts_treated_as_zero(self):
        """Non-numeric or missing amounts become zero."""
        df = pd.DataFrame({
            "order_date": ["2021-01-01", "2021-01-02", "2021-01-03"],
            "amount": [100.0, "invalid", pd.NA],
            "status": ["completed", "shipped", "delivered"],
        })
        result = calculate_monthly_revenue(df)
        expected = pd.DataFrame({
            "month": ["2021-01"],
            "revenue": [100.0],
        })
        pd.testing.assert_frame_equal(result, expected)

    def test_all_orders_cancelled(self):
        """When all orders are cancelled, result should be empty with correct columns."""
        df = pd.DataFrame({
            "order_date": ["2021-01-01", "2021-02-01"],
            "amount": [10.0, 20.0],
            "status": ["cancelled", "CANCELADO"],
        })
        result = calculate_monthly_revenue(df)
        expected = pd.DataFrame({
            "month": pd.Series(dtype="object"),
            "revenue": pd.Series(dtype="float64"),
        })
        pd.testing.assert_frame_equal(result, expected)

    def test_empty_dataframe(self):
        """Empty input DataFrame should produce empty output."""
        df = pd.DataFrame(columns=["order_date", "amount", "status"])
        result = calculate_monthly_revenue(df)
        expected = pd.DataFrame({
            "month": pd.Series(dtype="object"),
            "revenue": pd.Series(dtype="float64"),
        })
        pd.testing.assert_frame_equal(result, expected)

    def test_duplicate_months_summed(self):
        """Multiple orders in same month are aggregated correctly."""
        df = pd.DataFrame({
            "order_date": ["2021-01-01", "2021-01-15", "2021-01-20"],
            "amount": [10.0, 20.0, 30.0],
            "status": ["completed", "shipped", "delivered"],
        })
        result = calculate_monthly_revenue(df)
        expected = pd.DataFrame({
            "month": ["2021-01"],
            "revenue": [60.0],
        })
        pd.testing.assert_frame_equal(result, expected)

    def test_sorting_by_month(self):
        """Result must be sorted by month in ascending order."""
        df = pd.DataFrame({
            "order_date": ["2021-03-01", "2021-01-01", "2021-02-01"],
            "amount": [30.0, 10.0, 20.0],
            "status": ["delivered", "shipped", "completed"],
        })
        result = calculate_monthly_revenue(df)
        expected = pd.DataFrame({
            "month": ["2021-01", "2021-02", "2021-03"],
            "revenue": [10.0, 20.0, 30.0],
        })
        pd.testing.assert_frame_equal(result, expected)

    def test_custom_column_names(self):
        """Function works with custom column names."""
        df = pd.DataFrame({
            "date": ["2021-01-01", "2021-01-02"],
            "value": [100.0, 200.0],
            "order_status": ["completed", "cancelled"],
        })
        result = calculate_monthly_revenue(df, date_col="date", amount_col="value", status_col="order_status")
        expected = pd.DataFrame({
            "month": ["2021-01"],
            "revenue": [100.0],
        })
        pd.testing.assert_frame_equal(result, expected)

    def test_nan_in_dates_and_amounts(self):
        """Mixed NaN in dates and amounts properly handled."""
        df = pd.DataFrame({
            "order_date": [pd.NaT, "2021-01-01", None],
            "amount": [50.0, pd.NA, 100.0],
            "status": ["shipped", "delivered", "cancelled"],
        })
        result = calculate_monthly_revenue(df)
        # Only row with valid date and not cancelled: second row (2021-01-01, amount=0 because NA treated as 0)
        expected = pd.DataFrame({
            "month": ["2021-01"],
            "revenue": [0.0],
        })
        pd.testing.assert_frame_equal(result, expected)

    def test_dataframe_with_extra_columns(self):
        """Extra columns in input should not affect output."""
        df = pd.DataFrame({
            "order_date": ["2021-01-01", "2021-01-02"],
            "amount": [10.0, 20.0],
            "status": ["completed", "shipped"],
            "extra1": ["a", "b"],
            "extra2": [1, 2],
        })
        result = calculate_monthly_revenue(df)
        expected = pd.DataFrame({
            "month": ["2021-01"],
            "revenue": [30.0],
        })
        pd.testing.assert_frame_equal(result, expected)