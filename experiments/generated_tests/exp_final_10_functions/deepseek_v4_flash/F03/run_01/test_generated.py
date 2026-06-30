import pandas as pd
import pytest
from ise26.targets import calculate_monthly_revenue


def test_basic_aggregation():
    df = pd.DataFrame({
        "order_date": ["2023-01-15", "2023-01-20", "2023-02-10"],
        "amount": [100.0, 200.0, 300.0],
        "status": ["completed", "completed", "completed"]
    })
    result = calculate_monthly_revenue(df)
    expected = pd.DataFrame({
        "month": pd.Series(["2023-01", "2023-02"], dtype="string"),
        "revenue": [300.0, 300.0]
    })
    pd.testing.assert_frame_equal(result, expected, check_dtype=True)


def test_cancelled_ignored():
    df = pd.DataFrame({
        "order_date": ["2023-01-01", "2023-01-02", "2023-01-03"],
        "amount": [10.0, 20.0, 30.0],
        "status": ["completed", "cancelled", "canceled"]
    })
    result = calculate_monthly_revenue(df)
    expected = pd.DataFrame({
        "month": pd.Series(["2023-01"], dtype="string"),
        "revenue": [10.0]
    })
    pd.testing.assert_frame_equal(result, expected)


def test_cancelled_ignored_portuguese():
    df = pd.DataFrame({
        "order_date": ["2023-01-01"],
        "amount": [100.0],
        "status": [" cancelado "]
    })
    result = calculate_monthly_revenue(df)
    assert result.empty
    assert result["month"].dtype == "string"
    assert result["revenue"].dtype == "float64"


def test_cancelled_case_surrounding_spaces():
    df = pd.DataFrame({
        "order_date": ["2023-01-01", "2023-01-02"],
        "amount": [100.0, 200.0],
        "status": [" CaNcElLeD ", "  COMPLETED  "]
    })
    result = calculate_monthly_revenue(df)
    expected = pd.DataFrame({
        "month": pd.Series(["2023-01"], dtype="string"),
        "revenue": [200.0]
    })
    pd.testing.assert_frame_equal(result, expected)


def test_invalid_dates_ignored():
    df = pd.DataFrame({
        "order_date": ["2023-01-01", "invalid", None, "2023-01-02"],
        "amount": [10.0, 20.0, 30.0, 40.0],
        "status": ["completed", "completed", "completed", "completed"]
    })
    result = calculate_monthly_revenue(df)
    expected = pd.DataFrame({
        "month": pd.Series(["2023-01"], dtype="string"),
        "revenue": [50.0]
    })
    pd.testing.assert_frame_equal(result, expected)


def test_invalid_amounts_treated_as_zero():
    df = pd.DataFrame({
        "order_date": ["2023-01-01", "2023-01-02"],
        "amount": ["abc", None],
        "status": ["completed", "completed"]
    })
    result = calculate_monthly_revenue(df)
    expected = pd.DataFrame({
        "month": pd.Series(["2023-01"], dtype="string"),
        "revenue": [0.0]
    })
    pd.testing.assert_frame_equal(result, expected)


def test_mixed_valid_and_invalid_all_rows_removed():
    df = pd.DataFrame({
        "order_date": [None, "invalid"],
        "amount": [10.0, 20.0],
        "status": ["completed", "cancelled"]
    })
    result = calculate_monthly_revenue(df)
    assert result.empty
    assert list(result.columns) == ["month", "revenue"]


def test_empty_dataframe_returns_empty_result():
    df = pd.DataFrame(columns=["order_date", "amount", "status"])
    result = calculate_monthly_revenue(df)
    assert result.empty
    assert result["month"].dtype == "string"
    assert result["revenue"].dtype == "float64"


def test_sorting_order():
    df = pd.DataFrame({
        "order_date": ["2023-03-01", "2023-01-01", "2023-02-01"],
        "amount": [30.0, 10.0, 20.0],
        "status": ["completed", "completed", "completed"]
    })
    result = calculate_monthly_revenue(df)
    expected = pd.DataFrame({
        "month": pd.Series(["2023-01", "2023-02", "2023-03"], dtype="string"),
        "revenue": [10.0, 20.0, 30.0]
    })
    pd.testing.assert_frame_equal(result, expected)


def test_dtypes_correctness():
    df = pd.DataFrame({
        "order_date": ["2023-01-01"],
        "amount": [100.0],
        "status": ["completed"]
    })
    result = calculate_monthly_revenue(df)
    assert result["month"].dtype == "string"
    assert result["revenue"].dtype == "float64"


def test_stable_sort_with_duplicate_months():
    df = pd.DataFrame({
        "order_date": ["2023-01-01", "2023-01-02"],
        "amount": [10.0, 20.0],
        "status": ["completed", "completed"]
    })
    result = calculate_monthly_revenue(df)
    expected = pd.DataFrame({
        "month": pd.Series(["2023-01"], dtype="string"),
        "revenue": [30.0]
    })
    pd.testing.assert_frame_equal(result, expected)