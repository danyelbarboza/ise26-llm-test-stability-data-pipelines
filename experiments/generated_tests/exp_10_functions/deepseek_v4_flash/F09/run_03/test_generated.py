import pandas as pd
import numpy as np
import pytest
from ise26.targets import cap_outliers_iqr


def test_no_outliers():
    """Values within IQR bounds remain unchanged."""
    df = pd.DataFrame({"amount": [10, 20, 30, 40, 50]})
    result = cap_outliers_iqr(df)
    expected = pd.Series([10.0, 20.0, 30.0, 40.0, 50.0], dtype="Float64", name="amount_capped")
    pd.testing.assert_series_equal(result["amount_capped"], expected)


def test_outliers_capped():
    """Values beyond 1.5*IQR are capped to the whiskers."""
    # Q1=2, Q3=28, IQR=26, lower=2-39=-37, upper=28+39=67
    # Outlier 100 -> 67, outlier -50 -> -37
    df = pd.DataFrame({"amount": [1, 2, 3, 10, 28, 30, 100, -50]})
    result = cap_outliers_iqr(df)
    expected = pd.Series(
        [1.0, 2.0, 3.0, 10.0, 28.0, 30.0, 67.0, -37.0],
        dtype="Float64",
        name="amount_capped",
    )
    pd.testing.assert_series_equal(result["amount_capped"], expected)


def test_missing_values():
    """NaN values become <NA> in the capped column."""
    df = pd.DataFrame({"amount": [1.0, np.nan, 3.0, None, 5.0]})
    result = cap_outliers_iqr(df)
    expected = pd.Series([1.0, pd.NA, 3.0, pd.NA, 5.0], dtype="Float64", name="amount_capped")
    pd.testing.assert_series_equal(result["amount_capped"], expected)


def test_non_numeric_values():
    """Non-numeric values coerce to NaN -> <NA> in output."""
    df = pd.DataFrame({"amount": [1, "abc", 3, None, 5]})
    result = cap_outliers_iqr(df)
    expected = pd.Series([1.0, pd.NA, 3.0, pd.NA, 5.0], dtype="Float64", name="amount_capped")
    pd.testing.assert_series_equal(result["amount_capped"], expected)


def test_all_invalid():
    """All missing/invalid values produce all <NA>."""
    df = pd.DataFrame({"amount": [np.nan, None, "x"]})
    result = cap_outliers_iqr(df)
    expected = pd.Series([pd.NA, pd.NA, pd.NA], dtype="Float64", name="amount_capped")
    pd.testing.assert_series_equal(result["amount_capped"], expected)


def test_empty_valid_values():
    """Empty valid (all NaN) returns all <NA>."""
    df = pd.DataFrame({"amount": [np.nan, np.nan]})
    result = cap_outliers_iqr(df)
    expected = pd.Series([pd.NA, pd.NA], dtype="Float64", name="amount_capped")
    pd.testing.assert_series_equal(result["amount_capped"], expected)


def test_single_value():
    """Only one valid number: IQR=0, bounds equal value, no capping."""
    df = pd.DataFrame({"amount": [42]})
    result = cap_outliers_iqr(df)
    expected = pd.Series([42.0], dtype="Float64", name="amount_capped")
    pd.testing.assert_series_equal(result["amount_capped"], expected)


def test_duplicate_values():
    """Duplicates do not affect IQR logic."""
    df = pd.DataFrame({"amount": [10, 10, 20, 20, 100]})
    result = cap_outliers_iqr(df)
    # Q1=10, Q3=20, IQR=10 => lower= -5, upper=35 -> cap 100 to 35
    expected = pd.Series([10.0, 10.0, 20.0, 20.0, 35.0], dtype="Float64", name="amount_capped")
    pd.testing.assert_series_equal(result["amount_capped"], expected)


def test_zero_variance():
    """All identical values produce no capping."""
    df = pd.DataFrame({"amount": [5, 5, 5]})
    result = cap_outliers_iqr(df)
    expected = pd.Series([5.0, 5.0, 5.0], dtype="Float64", name="amount_capped")
    pd.testing.assert_series_equal(result["amount_capped"], expected)


def test_negative_and_outliers():
    """Negative values and outliers capped correctly."""
    df = pd.DataFrame({"amount": [-100, -10, -5, 0, 10, 200]})
    result = cap_outliers_iqr(df)
    # Q1=-10, Q3=10, IQR=20 => lower=-10-30=-40, upper=10+30=40
    # cap -100 to -40, 200 to 40
    expected = pd.Series([-40.0, -10.0, -5.0, 0.0, 10.0, 40.0], dtype="Float64", name="amount_capped")
    pd.testing.assert_series_equal(result["amount_capped"], expected)


def test_mixed_types():
    """Int and float values handled properly."""
    df = pd.DataFrame({"amount": [1, 2.5, 3, 4.7, 100]})
    result = cap_outliers_iqr(df)
    # Q1=2.5, Q3=4.7, IQR=2.2 => lower=-0.8, upper=8.0 -> cap 100 to 8.0
    expected = pd.Series([1.0, 2.5, 3.0, 4.7, 8.0], dtype="Float64", name="amount_capped")
    pd.testing.assert_series_equal(result["amount_capped"], expected)


def test_output_dtype_float64():
    """Capped column must be Float64 (nullable float)."""
    df = pd.DataFrame({"amount": [1, 2, 3]})
    result = cap_outliers_iqr(df)
    assert result["amount_capped"].dtype == "Float64"
    assert result["amount_capped"].isna().sum() == 0


def test_original_column_unchanged():
    """The input column must not be mutated."""
    df = pd.DataFrame({"amount": [1.0, 2.0, 100.0]})
    original = df["amount"].copy()
    result = cap_outliers_iqr(df)
    pd.testing.assert_series_equal(df["amount"], original)


def test_default_parameters():
    """Default column names ('amount' and 'amount_capped')."""
    df = pd.DataFrame({"amount": [1, 2, 3]})
    result = cap_outliers_iqr(df)
    assert "amount_capped" in result.columns
    assert result["amount_capped"].notna().all()


def test_custom_column_names():
    """Custom value_col and output_col."""
    df = pd.DataFrame({"val": [10, 20, 30, 100]})
    result = cap_outliers_iqr(df, value_col="val", output_col="capped")
    # Q1=10, Q3=30, IQR=20 -> lower=-20, upper=60 -> cap 100 to 60
    expected = pd.Series([10.0, 20.0, 30.0, 60.0], dtype="Float64", name="capped")
    pd.testing.assert_series_equal(result["capped"], expected)


def test_new_dataframe_returned():
    """A new DataFrame is returned, not the original one."""
    df = pd.DataFrame({"amount": [1, 2, 3]})
    result = cap_outliers_iqr(df)
    assert result is not df
    assert list(result.columns) == ["amount", "amount_capped"]


def test_large_outliers():
    """Large positive and negative values capped correctly."""
    df = pd.DataFrame({"amount": [-1e9, 0, 10, 20, 30, 1e9]})
    result = cap_outliers_iqr(df)
    # Q1=0, Q3=20, IQR=20 -> lower=-30, upper=50 -> cap -1e9 to -30, 1e9 to 50
    expected = pd.Series([-30.0, 0.0, 10.0, 20.0, 30.0, 50.0], dtype="Float64", name="amount_capped")
    pd.testing.assert_series_equal(result["amount_capped"], expected)


def test_missing_and_outliers():
    """Outliers and missing values coexist."""
    df = pd.DataFrame({"amount": [1.0, np.nan, 100.0, None, 50.0]})
    result = cap_outliers_iqr(df)
    # Q1=1, Q3=50, IQR=49 -> lower=1-73.5=-72.5, upper=50+73.5=123.5 -> 100 stays
    expected = pd.Series([1.0, pd.NA, 100.0, pd.NA, 50.0], dtype="Float64", name="amount_capped")
    pd.testing.assert_series_equal(result["amount_capped"], expected)