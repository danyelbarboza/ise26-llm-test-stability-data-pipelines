import pandas as pd
import numpy as np
import pytest
from ise26.targets import calculate_monthly_revenue


def test_basic_monthly_revenue():
    """Test basic aggregation of valid orders by month."""
    df = pd.DataFrame({
        'order_date': pd.to_datetime(['2023-01-15', '2023-01-20', '2023-02-10']),
        'amount': [100.0, 200.0, 300.0],
        'status': ['completed', 'shipped', 'delivered'],
    })
    result = calculate_monthly_revenue(df)
    expected = pd.DataFrame({
        'month': ['2023-01', '2023-02'],
        'revenue': [300.0, 300.0],
    })
    pd.testing.assert_frame_equal(result, expected)


def test_canceled_orders_excluded():
    """Test that canceled orders (English, Portuguese, case, spaces) are excluded."""
    df = pd.DataFrame({
        'order_date': pd.to_datetime(['2023-01-15', '2023-01-20', '2023-02-10', '2023-02-15']),
        'amount': [100.0, 200.0, 300.0, 400.0],
        'status': ['Cancelled', ' canceled ', 'CANCELADO', 'active'],
    })
    result = calculate_monthly_revenue(df)
    # Only the last order with status 'active' should be counted in Feb
    expected = pd.DataFrame({
        'month': ['2023-02'],
        'revenue': [400.0],
    })
    pd.testing.assert_frame_equal(result, expected)


def test_invalid_dates_excluded():
    """Test that rows with invalid dates are ignored."""
    df = pd.DataFrame({
        'order_date': ['2023-01-15', 'not_a_date', None, '2023-02-10'],
        'amount': [100.0, 200.0, 300.0, 400.0],
        'status': ['completed', 'shipped', 'delivered', 'active'],
    })
    result = calculate_monthly_revenue(df)
    expected = pd.DataFrame({
        'month': ['2023-01', '2023-02'],
        'revenue': [100.0, 400.0],
    })
    pd.testing.assert_frame_equal(result, expected)


def test_invalid_amounts_treated_as_zero():
    """Test that invalid/missing amounts are treated as zero."""
    df = pd.DataFrame({
        'order_date': pd.to_datetime(['2023-01-15', '2023-01-20', '2023-02-10']),
        'amount': [100.0, None, 'invalid'],
        'status': ['completed', 'shipped', 'delivered'],
    })
    result = calculate_monthly_revenue(df)
    # Only first order contributes 100, others zero
    expected = pd.DataFrame({
        'month': ['2023-01', '2023-02'],
        'revenue': [100.0, 0.0],
    })
    pd.testing.assert_frame_equal(result, expected)


def test_duplicate_months_aggregated():
    """Test that multiple orders in same month are summed."""
    df = pd.DataFrame({
        'order_date': pd.to_datetime(['2023-01-01', '2023-01-15', '2023-01-31']),
        'amount': [10.0, 20.0, 30.0],
        'status': ['a', 'b', 'c'],
    })
    result = calculate_monthly_revenue(df)
    expected = pd.DataFrame({
        'month': ['2023-01'],
        'revenue': [60.0],
    })
    pd.testing.assert_frame_equal(result, expected)


def test_empty_dataframe():
    """Test that an empty DataFrame returns empty result with correct columns."""
    df = pd.DataFrame(columns=['order_date', 'amount', 'status'])
    result = calculate_monthly_revenue(df)
    assert result.empty
    assert list(result.columns) == ['month', 'revenue']


def test_no_valid_orders():
    """Test when all orders are canceled or invalid dates."""
    df = pd.DataFrame({
        'order_date': ['invalid', None],
        'amount': [100.0, 200.0],
        'status': ['canceled', 'cancelado'],
    })
    result = calculate_monthly_revenue(df)
    expected = pd.DataFrame(columns=['month', 'revenue'])
    pd.testing.assert_frame_equal(result, expected, check_dtype=False)


def test_sorting_by_month():
    """Test the result is sorted by month ascending."""
    df = pd.DataFrame({
        'order_date': pd.to_datetime(['2023-03-01', '2023-01-01', '2023-02-01']),
        'amount': [10.0, 20.0, 30.0],
        'status': ['ok', 'ok', 'ok'],
    })
    result = calculate_monthly_revenue(df)
    assert result['month'].tolist() == ['2023-01', '2023-02', '2023-03']


def test_custom_column_names():
    """Test with non-default column names."""
    df = pd.DataFrame({
        'date': pd.to_datetime(['2023-01-01', '2023-02-01']),
        'value': [100.0, 200.0],
        'state': ['pending', 'cancelled'],
    })
    result = calculate_monthly_revenue(df, date_col='date', amount_col='value', status_col='state')
    expected = pd.DataFrame({
        'month': ['2023-01'],
        'revenue': [100.0],
    })
    pd.testing.assert_frame_equal(result, expected)


def test_mixed_statuses():
    """Test with a mix of valid, canceled, and other statuses."""
    df = pd.DataFrame({
        'order_date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-02-01']),
        'amount': [10, 20, 30, 40],
        'status': ['completed', 'Cancelled', 'Cancelado ', 'shipped'],
    })
    result = calculate_monthly_revenue(df)
    expected = pd.DataFrame({
        'month': ['2023-01', '2023-02'],
        'revenue': [40.0, 40.0],
    })
    pd.testing.assert_frame_equal(result, expected)


def test_case_insensitive_status():
    """Test that status normalization ignores case and extra spaces."""
    df = pd.DataFrame({
        'order_date': pd.to_datetime(['2023-01-01', '2023-01-02']),
        'amount': [100, 200],
        'status': ['  CaNcElAdO   ', 'CANCELED'],
    })
    result = calculate_monthly_revenue(df)
    expected = pd.DataFrame(columns=['month', 'revenue'])
    pd.testing.assert_frame_equal(result, expected, check_dtype=False)


def test_revenue_column_type():
    """Test that revenue column is numeric (float)."""
    df = pd.DataFrame({
        'order_date': pd.to_datetime(['2023-01-01']),
        'amount': [100],
        'status': ['ok'],
    })
    result = calculate_monthly_revenue(df)
    assert result['revenue'].dtype == float


def test_single_order():
    """Test with a single valid order."""
    df = pd.DataFrame({
        'order_date': pd.to_datetime(['2023-05-20']),
        'amount': [99.99],
        'status': ['shipped'],
    })
    result = calculate_monthly_revenue(df)
    expected = pd.DataFrame({
        'month': ['2023-05'],
        'revenue': [99.99],
    })
    pd.testing.assert_frame_equal(result, expected)