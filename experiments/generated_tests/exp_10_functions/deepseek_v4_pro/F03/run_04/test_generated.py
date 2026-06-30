import pytest
import pandas as pd
from ise26.targets import calculate_monthly_revenue


def test_basic_aggregation():
    """Valid orders with no cancelations should be aggregated by month."""
    df = pd.DataFrame({
        "order_date": ["2023-01-05", "2023-01-15", "2023-02-10"],
        "amount": [100, 200, 300],
        "status": ["completed", "completed", "completed"],
    })
    result = calculate_monthly_revenue(df)
    expected = pd.DataFrame({
        "month": ["2023-01", "2023-02"],
        "revenue": [300, 300],
    })
    pd.testing.assert_frame_equal(result, expected)


def test_canceled_orders_excluded():
    """Orders with canceled status (English, Portuguese, case, spaces) must be ignored."""
    df = pd.DataFrame({
        "order_date": ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05"],
        "amount": [10, 20, 30, 40, 50],
        "status": [
            "Cancelled",
            "  CANCELLED  ",
            "cancelado",
            "Canceled",
            "active",
        ],
    })
    result = calculate_monthly_revenue(df)
    expected = pd.DataFrame({
        "month": ["2023-01"],
        "revenue": [50],  # only the "active" order remains
    })
    pd.testing.assert_frame_equal(result, expected)


def test_invalid_dates_excluded():
    """Rows where order_date cannot be parsed should be ignored."""
    df = pd.DataFrame({
        "order_date": ["2023-01-10", "not-a-date", "2023-01-20", None],
        "amount": [100, 200, 300, 400],
        "status": ["ok", "ok", "ok", "ok"],
    })
    result = calculate_monthly_revenue(df)
    expected = pd.DataFrame({
        "month": ["2023-01"],
        "revenue": [400],  # only two valid dates
    })
    pd.testing.assert_frame_equal(result, expected)


def test_invalid_amounts_treated_as_zero():
    """Non‑numeric amounts become zero and do not cause errors; they still contribute (0) to the sum."""
    df = pd.DataFrame({
        "order_date": ["2023-01-01", "2023-01-02"],
        "amount": ["not a number", 50],
        "status": ["ok", "ok"],
    })
    result = calculate_monthly_revenue(df)
    expected = pd.DataFrame({
        "month": ["2023-01"],
        "revenue": [50],  # 0 + 50
    })
    pd.testing.assert_frame_equal(result, expected)


def test_missing_amounts_treated_as_zero():
    """NaN amounts are filled with 0 and included in the aggregation."""
    df = pd.DataFrame({
        "order_date": ["2023-03-15", "2023-03-20"],
        "amount": [None, 75.5],
        "status": ["delivered", "delivered"],
    })
    result = calculate_monthly_revenue(df)
    expected = pd.DataFrame({
        "month": ["2023-03"],
        "revenue": [75.5],
    })
    pd.testing.assert_frame_equal(result, expected)


def test_mixed_invalid_and_canceled():
    """Rows with invalid dates or canceled status are excluded, others are kept."""
    df = pd.DataFrame({
        "order_date": ["2023-04-01", "bad-date", "2023-04-10", "2023-04-15"],
        "amount": [100, 200, 300, 400],
        "status": ["ok", "ok", "cancelado", "ok"],
    })
    result = calculate_monthly_revenue(df)
    expected = pd.DataFrame({
        "month": ["2023-04"],
        "revenue": [500],  # 100 (valid) + 400 (valid) = 500
    })
    pd.testing.assert_frame_equal(result, expected)


def test_all_canceled_returns_empty():
    """If every order is canceled, result DataFrame is empty (but has correct columns)."""
    df = pd.DataFrame({
        "order_date": ["2023-05-01", "2023-05-02"],
        "amount": [10, 20],
        "status": ["CANCELLED", "cancelado"],
    })
    result = calculate_monthly_revenue(df)
    expected = pd.DataFrame(columns=["month", "revenue"]).astype({"month": object, "revenue": float})
    pd.testing.assert_frame_equal(result, expected)


def test_all_invalid_dates_returns_empty():
    """If every date is unparseable, result is empty."""
    df = pd.DataFrame({
        "order_date": ["x", "y", None],
        "amount": [1, 2, 3],
        "status": ["ok", "ok", "ok"],
    })
    result = calculate_monthly_revenue(df)
    expected = pd.DataFrame(columns=["month", "revenue"]).astype({"month": object, "revenue": float})
    pd.testing.assert_frame_equal(result, expected)


def test_empty_input_returns_empty():
    """Empty DataFrame input yields empty result with required columns."""
    df = pd.DataFrame(columns=["order_date", "amount", "status"])
    result = calculate_monthly_revenue(df)
    expected = pd.DataFrame(columns=["month", "revenue"]).astype({"month": object, "revenue": float})
    pd.testing.assert_frame_equal(result, expected)


def test_sorting_order():
    """Result must be sorted by month string (YYYY-MM)."""
    df = pd.DataFrame({
        "order_date": ["2023-12-01", "2023-01-05", "2023-02-10", "2023-01-20"],
        "amount": [1, 1, 1, 1],
        "status": ["ok"] * 4,
    })
    result = calculate_monthly_revenue(df)
    expected_months = ["2023-01", "2023-02", "2023-12"]
    assert list(result["month"]) == expected_months
    assert list(result["revenue"]) == [2, 1, 1]


def test_custom_column_names():
    """The function should respect non-default column names."""
    df = pd.DataFrame({
        "data_venda": ["2023-03-03", "2023-03-04"],
        "valor": [100, 200],
        "situacao": ["ok", "Cancelado"],
    })
    result = calculate_monthly_revenue(df, date_col="data_venda", amount_col="valor", status_col="situacao")
    expected = pd.DataFrame({
        "month": ["2023-03"],
        "revenue": [100],  # only the first order is non-canceled
    })
    pd.testing.assert_frame_equal(result, expected)


def test_original_df_not_modified():
    """The input DataFrame should remain unchanged after the function call."""
    df = pd.DataFrame({
        "order_date": ["2023-06-01"],
        "amount": [42],
        "status": ["ok"],
    })
    df_copy = df.copy(deep=True)
    calculate_monthly_revenue(df)
    pd.testing.assert_frame_equal(df, df_copy)


def test_status_normalization_spaces_and_case():
    """Various representations of canceled should all be detected."""
    # All these should be treated as canceled.
    statuses = ["cancelled", "Cancelled", "  cancelled  ", "CANCELED", "cancelado", "CANCELADO"]
    df = pd.DataFrame({
        "order_date": ["2023-07-01"] * len(statuses),
        "amount": [10] * len(statuses),
        "status": statuses,
    })
    result = calculate_monthly_revenue(df)
    expected = pd.DataFrame(columns=["month", "revenue"]).astype({"month": object, "revenue": float})
    pd.testing.assert_frame_equal(result, expected)


def test_zero_revenue_handling():
    """When all amounts are invalid/missing (zeros), revenue should be zero."""
    df = pd.DataFrame({
        "order_date": ["2023-08-01", "2023-08-02"],
        "amount": [None, "abc"],
        "status": ["ok", "ok"],
    })
    result = calculate_monthly_revenue(df)
    # Both become 0, so total revenue is 0.
    expected = pd.DataFrame({
        "month": ["2023-08"],
        "revenue": [0.0],
    })
    pd.testing.assert_frame_equal(result, expected)