import pytest
import pandas as pd
from ise26.targets import calculate_monthly_revenue


class TestCalculateMonthlyRevenue:
    """Test suite for calculate_monthly_revenue."""

    def test_basic_monthly_revenue(self):
        """Aggregate simple valid orders."""
        df = pd.DataFrame({
            "order_date": ["2023-01-15", "2023-01-20", "2023-02-10", "2023-03-05"],
            "amount": [100, 200, 150, 300],
            "status": ["delivered", "shipped", "delivered", "processing"],
        })
        result = calculate_monthly_revenue(df)
        expected = pd.DataFrame({
            "month": ["2023-01", "2023-02", "2023-03"],
            "revenue": [300, 150, 300],
        })
        pd.testing.assert_frame_equal(result, expected)

    def test_cancelled_in_english(self):
        """Rows with cancelled/canceled status in any case should be excluded."""
        df = pd.DataFrame({
            "order_date": ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04"],
            "amount": [100, 200, 300, 400],
            "status": ["cancelled", "canceled", "CANCELLED", " Canceled "],
        })
        result = calculate_monthly_revenue(df)
        expected = pd.DataFrame({"month": [], "revenue": []}).astype({"month": str, "revenue": float})
        pd.testing.assert_frame_equal(result, expected)

    def test_cancelled_in_portuguese(self):
        """Rows with cancelado status in any case/spacing should be excluded."""
        df = pd.DataFrame({
            "order_date": ["2023-02-01", "2023-02-02"],
            "amount": [50, 60],
            "status": ["cancelado", " Cancelado "],
        })
        result = calculate_monthly_revenue(df)
        expected = pd.DataFrame({"month": [], "revenue": []}).astype({"month": str, "revenue": float})
        pd.testing.assert_frame_equal(result, expected)

    def test_invalid_dates_ignored(self):
        """Rows with invalid order dates should be skipped."""
        df = pd.DataFrame({
            "order_date": ["2023-01-01", "invalid_date", None, "2023-01-02"],
            "amount": [100, 200, 300, 400],
            "status": ["delivered", "delivered", "delivered", "shipped"],
        })
        result = calculate_monthly_revenue(df)
        # Only first and last rows have valid dates
        expected = pd.DataFrame({
            "month": ["2023-01", "2023-01"],
            "revenue": [100, 400],
        }).groupby("month", as_index=False).sum()
        expected = expected.sort_values("month").reset_index(drop=True)
        pd.testing.assert_frame_equal(result, expected)

    def test_invalid_amounts_treated_as_zero(self):
        """Non-numeric or missing amounts should be treated as 0."""
        df = pd.DataFrame({
            "order_date": ["2023-01-01", "2023-01-02", "2023-01-03"],
            "amount": ["abc", None, "100"],
            "status": ["delivered", "delivered", "delivered"],
        })
        result = calculate_monthly_revenue(df)
        expected = pd.DataFrame({
            "month": ["2023-01"],
            "revenue": [100],  # 0 + 0 + 100
        })
        pd.testing.assert_frame_equal(result, expected)

    def test_mixed_statuses_filters_canceled_only(self):
        """Valid order amounts are summed, canceled rows ignored."""
        df = pd.DataFrame({
            "order_date": ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04"],
            "amount": [10, 20, 30, 40],
            "status": ["delivered", "cancelled", "shipped", "cancelado"],
        })
        result = calculate_monthly_revenue(df)
        expected = pd.DataFrame({
            "month": ["2023-01"],
            "revenue": [40],  # 10 + 30
        })
        pd.testing.assert_frame_equal(result, expected)

    def test_empty_dataframe(self):
        """Empty input yields empty result with correct columns."""
        df = pd.DataFrame({"order_date": [], "amount": [], "status": []})
        result = calculate_monthly_revenue(df)
        expected = pd.DataFrame({"month": pd.Series(dtype=str), "revenue": pd.Series(dtype=float)})
        pd.testing.assert_frame_equal(result, expected)

    def test_all_cancelled_or_invalid_returns_empty(self):
        """No valid rows leads to empty DataFrame."""
        df = pd.DataFrame({
            "order_date": ["2023-01-01", "2023-01-02"],
            "amount": [100, 200],
            "status": ["cancelled", "cancelado"],
        })
        result = calculate_monthly_revenue(df)
        expected = pd.DataFrame({"month": pd.Series(dtype=str), "revenue": pd.Series(dtype=float)})
        pd.testing.assert_frame_equal(result, expected)

    def test_ordering_by_month(self):
        """Result should be sorted by month even if input is not in order."""
        df = pd.DataFrame({
            "order_date": ["2023-03-01", "2023-01-01", "2023-02-01"],
            "amount": [100, 200, 300],
            "status": ["delivered", "delivered", "delivered"],
        })
        result = calculate_monthly_revenue(df)
        expected = pd.DataFrame({
            "month": ["2023-01", "2023-02", "2023-03"],
            "revenue": [200, 300, 100],
        })
        pd.testing.assert_frame_equal(result, expected)

    def test_na_status_not_cancelled(self):
        """Null status is not treated as cancelled."""
        df = pd.DataFrame({
            "order_date": ["2023-01-01", "2023-01-02"],
            "amount": [100, 200],
            "status": [None, "cancelled"],
        })
        result = calculate_monthly_revenue(df)
        expected = pd.DataFrame({
            "month": ["2023-01"],
            "revenue": [100],
        })
        pd.testing.assert_frame_equal(result, expected)

    def test_duplicate_months_summed(self):
        """Multiple orders in the same month should be summed."""
        df = pd.DataFrame({
            "order_date": ["2023-01-01", "2023-01-15", "2023-01-25"],
            "amount": [50, 75, 100],
            "status": ["delivered", "shipped", "delivered"],
        })
        result = calculate_monthly_revenue(df)
        expected = pd.DataFrame({
            "month": ["2023-01"],
            "revenue": [225],
        })
        pd.testing.assert_frame_equal(result, expected)

    def test_custom_column_names(self):
        """Function should work with custom column names."""
        df = pd.DataFrame({
            "dt": ["2023-01-01", "2023-02-01"],
            "val": [100, 200],
            "stat": ["delivered", "cancelled"],
        })
        result = calculate_monthly_revenue(df, date_col="dt", amount_col="val", status_col="stat")
        expected = pd.DataFrame({
            "month": ["2023-01"],
            "revenue": [100],
        })
        pd.testing.assert_frame_equal(result, expected)