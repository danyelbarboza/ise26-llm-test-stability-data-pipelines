import pytest
import pandas as pd
from ise26.targets import calculate_monthly_revenue


def test_basic_monthly_revenue():
    # Normal orders, some cancelled in various forms
    data = {
        "order_date": ["2023-01-05", "2023-01-15", "2023-02-10", "2023-02-20"],
        "amount": [100.0, 200.0, 300.0, 400.0],
        "status": ["delivered", "cancelled", "completed", "cancelado"],
    }
    df = pd.DataFrame(data)
    result = calculate_monthly_revenue(df)
    expected = pd.DataFrame({"month": ["2023-01", "2023-02"], "revenue": [100.0, 300.0]})
    pd.testing.assert_frame_equal(result, expected)


def test_cancel_variants():
    # Test all known cancellation forms (English and Portuguese, case and spaces)
    data = {
        "order_date": ["2023-03-01", "2023-03-02", "2023-03-03", "2023-03-04", "2023-03-05", "2023-03-06"],
        "amount": [10.0, 20.0, 30.0, 40.0, 50.0, 60.0],
        "status": ["cancelled", "canceled", "cancelado", " Cancelled ", "CANCELADO", "c anceled"],
    }
    df = pd.DataFrame(data)
    result = calculate_monthly_revenue(df)
    # All should be cancelled, so no revenue
    assert result.empty
    assert list(result.columns) == ["month", "revenue"]


def test_nan_amounts():
    # Missing or invalid amounts treated as zero
    data = {
        "order_date": ["2023-04-01", "2023-04-01", "2023-04-02", "2023-04-02"],
        "amount": [100.0, None, "invalid", 200.0],
        "status": ["delivered", "delivered", "delivered", "cancelled"],
    }
    df = pd.DataFrame(data)
    result = calculate_monthly_revenue(df)
    # Only rows with valid non-cancelled: first row amount 100, second row amount 0 (None->0), third row amount 0 (invalid->0) but third row status is cancelled? Actually third row is "delivered" and amount "invalid" -> 0. Fourth is cancelled.
    # So expected revenue = 100 (first) + 0 (second) + 0 (third) = 100
    expected = pd.DataFrame({"month": ["2023-04"], "revenue": [100.0]})
    pd.testing.assert_frame_equal(result, expected)


def test_invalid_dates_ignored():
    data = {
        "order_date": ["2023-05-01", "not_a_date", None, "2023-05-15"],
        "amount": [50.0, 100.0, 200.0, 300.0],
        "status": ["delivered", "delivered", "delivered", "cancelled"],
    }
    df = pd.DataFrame(data)
    result = calculate_monthly_revenue(df)
    # Only first row is valid non-cancelled; second and third have invalid dates; fourth is cancelled
    expected = pd.DataFrame({"month": ["2023-05"], "revenue": [50.0]})
    pd.testing.assert_frame_equal(result, expected)


def test_all_cancelled_or_invalid():
    data = {
        "order_date": ["2023-06-01", "2023-06-02"],
        "amount": [10.0, 20.0],
        "status": ["cancelled", "cancelled"],
    }
    df = pd.DataFrame(data)
    result = calculate_monthly_revenue(df)
    assert result.empty
    assert list(result.columns) == ["month", "revenue"]


def test_duplicate_months():
    data = {
        "order_date": ["2023-07-01", "2023-07-15", "2023-07-20"],
        "amount": [100.0, 200.0, 300.0],
        "status": ["delivered", "delivered", "delivered"],
    }
    df = pd.DataFrame(data)
    result = calculate_monthly_revenue(df)
    expected = pd.DataFrame({"month": ["2023-07"], "revenue": [600.0]})
    pd.testing.assert_frame_equal(result, expected)


def test_sorting():
    data = {
        "order_date": ["2023-09-01", "2023-08-01", "2023-10-01"],
        "amount": [100.0, 200.0, 300.0],
        "status": ["delivered", "delivered", "delivered"],
    }
    df = pd.DataFrame(data)
    result = calculate_monthly_revenue(df)
    expected = pd.DataFrame({"month": ["2023-08", "2023-09", "2023-10"], "revenue": [200.0, 100.0, 300.0]})
    pd.testing.assert_frame_equal(result, expected)


def test_custom_column_names():
    data = {
        "date": ["2023-11-01", "2023-11-02"],
        "val": [50.0, 100.0],
        "stat": ["delivered", "cancelled"],
    }
    df = pd.DataFrame(data)
    result = calculate_monthly_revenue(df, date_col="date", amount_col="val", status_col="stat")
    expected = pd.DataFrame({"month": ["2023-11"], "revenue": [50.0]})
    pd.testing.assert_frame_equal(result, expected)


def test_non_cancel_status_with_cancel_substring():
    # Status containing "cancel" but not exact normalized match should not be cancelled
    data = {
        "order_date": ["2023-12-01"],
        "amount": [999.0],
        "status": ["pre-cancelled"],
    }
    df = pd.DataFrame(data)
    result = calculate_monthly_revenue(df)
    # " pre-cancelled " normalized -> "pre-cancelled", not in cancelled set
    expected = pd.DataFrame({"month": ["2023-12"], "revenue": [999.0]})
    pd.testing.assert_frame_equal(result, expected)


def test_empty_dataframe():
    df = pd.DataFrame({"order_date": [], "amount": [], "status": []})
    result = calculate_monthly_revenue(df)
    assert result.empty
    assert list(result.columns) == ["month", "revenue"]


def test_mixed_types_amount():
    # Amount as strings that can be coerced, others as floats
    data = {
        "order_date": ["2024-01-01", "2024-01-02"],
        "amount": ["150", 200.0],
        "status": ["delivered", "cancelled"],
    }
    df = pd.DataFrame(data)
    result = calculate_monthly_revenue(df)
    expected = pd.DataFrame({"month": ["2024-01"], "revenue": [150.0]})
    pd.testing.assert_frame_equal(result, expected)