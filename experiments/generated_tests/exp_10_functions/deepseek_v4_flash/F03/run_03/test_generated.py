import pandas as pd
import pytest
from ise26.targets import calculate_monthly_revenue


def test_basic_revenue():
    df = pd.DataFrame({
        'order_date': ['2023-01-15', '2023-01-20', '2023-02-10'],
        'amount': [100, 200, 300],
        'status': ['delivered', 'delivered', 'shipped']
    })
    result = calculate_monthly_revenue(df)
    expected = pd.DataFrame({
        'month': ['2023-01', '2023-02'],
        'revenue': [300, 300]
    })
    pd.testing.assert_frame_equal(result, expected)


def test_canceled_orders_excluded():
    df = pd.DataFrame({
        'order_date': ['2023-01-15', '2023-01-20', '2023-02-10'],
        'amount': [100, 200, 300],
        'status': ['delivered', 'CANCELED', 'cancelado ']
    })
    result = calculate_monthly_revenue(df)
    expected = pd.DataFrame({
        'month': ['2023-01'],
        'revenue': [100]
    })
    pd.testing.assert_frame_equal(result, expected)


def test_invalid_dates_ignored():
    df = pd.DataFrame({
        'order_date': ['2023-01-15', 'invalid-date', None, '2023-03-01'],
        'amount': [100, 200, 300, 400],
        'status': ['delivered', 'delivered', 'delivered', 'delivered']
    })
    result = calculate_monthly_revenue(df)
    expected = pd.DataFrame({
        'month': ['2023-01', '2023-03'],
        'revenue': [100, 400]
    })
    pd.testing.assert_frame_equal(result, expected)


def test_invalid_amounts_treated_as_zero():
    df = pd.DataFrame({
        'order_date': ['2023-01-15', '2023-01-20', '2023-02-10'],
        'amount': [100, 'not-a-number', None],
        'status': ['delivered', 'delivered', 'delivered']
    })
    result = calculate_monthly_revenue(df)
    expected = pd.DataFrame({
        'month': ['2023-01', '2023-02'],
        'revenue': [100, 0]
    })
    pd.testing.assert_frame_equal(result, expected)


def test_aggregation_same_month():
    df = pd.DataFrame({
        'order_date': ['2023-01-01', '2023-01-15', '2023-01-31'],
        'amount': [50, 75, 25],
        'status': ['delivered', 'delivered', 'delivered']
    })
    result = calculate_monthly_revenue(df)
    expected = pd.DataFrame({
        'month': ['2023-01'],
        'revenue': [150]
    })
    pd.testing.assert_frame_equal(result, expected)


def test_all_canceled_orders():
    df = pd.DataFrame({
        'order_date': ['2023-01-15'],
        'amount': [100],
        'status': ['cancelled']
    })
    result = calculate_monthly_revenue(df)
    expected = pd.DataFrame({
        'month': pd.Series([], dtype='object'),
        'revenue': pd.Series([], dtype='float64')
    })
    pd.testing.assert_frame_equal(result, expected)


def test_status_normalization():
    df = pd.DataFrame({
        'order_date': ['2023-01-15', '2023-01-20'],
        'amount': [100, 200],
        'status': ['  CANcelled  ', 'Cancelado']
    })
    result = calculate_monthly_revenue(df)
    expected = pd.DataFrame({
        'month': pd.Series([], dtype='object'),
        'revenue': pd.Series([], dtype='float64')
    })
    pd.testing.assert_frame_equal(result, expected)


def test_custom_column_names():
    df = pd.DataFrame({
        'dt': ['2023-01-15', '2023-02-10'],
        'amt': [100, 200],
        'sts': ['delivered', 'canceled']
    })
    result = calculate_monthly_revenue(df, date_col='dt', amount_col='amt', status_col='sts')
    expected = pd.DataFrame({
        'month': ['2023-01'],
        'revenue': [100]
    })
    pd.testing.assert_frame_equal(result, expected)


def test_output_is_sorted():
    df = pd.DataFrame({
        'order_date': ['2023-03-01', '2023-01-15', '2023-02-01'],
        'amount': [30, 10, 20],
        'status': ['delivered', 'delivered', 'delivered']
    })
    result = calculate_monthly_revenue(df)
    expected = pd.DataFrame({
        'month': ['2023-01', '2023-02', '2023-03'],
        'revenue': [10, 20, 30]
    })
    pd.testing.assert_frame_equal(result, expected)