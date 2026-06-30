import pytest
import pandas as pd
import numpy as np
from ise26.targets import cap_outliers_iqr


def test_basic_capping():
    """Normal numeric values with some outliers."""
    df = pd.DataFrame({"amount": [1, 2, 3, 4, 5, 100, 200]})
    result = cap_outliers_iqr(df, "amount", "capped")
    # Calculate IQR manually:
    # sorted: [1,2,3,4,5,100,200] -> Q1=2, Q3=100, IQR=98, LB=2-147=-145, UB=100+147=247
    # So all values are within bounds, except none are outside? Actually 100 and 200 are below UB=247, so all inside.
    # Let's test with clearer outliers: [1,2,3,4,5,100,200] - actually Q1=2, Q3=100, IQR=98, LB=-145, UB=247 -> no outliers
    # Need outlier beyond 247 or below -145. Use [10,12,14,16,18,20,1000]
    df2 = pd.DataFrame({"amount": [10, 12, 14, 16, 18, 20, 1000]})
    result2 = cap_outliers_iqr(df2, "amount", "capped")
    # Q1=12, Q3=20, IQR=8, LB=12-12=0, UB=20+12=32
    # Values: 10,12,14,16,18,20,1000 -> cap lower at 0? No values below 0, 1000 capped to 32.
    # Expected: [10,12,14,16,18,20,32]
    expected = [10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 32.0]
    assert result2["capped"].tolist() == expected


def test_lower_bound_capping():
    """Values below lower bound are capped."""
    df = pd.DataFrame({"amount": [-100, 10, 12, 14, 16, 18, 20]})
    result = cap_outliers_iqr(df, "amount", "capped")
    # Q1=12, Q3=18, IQR=6, LB=12-9=3, UB=18+9=27
    # -100 capped to 3, others within [3,27] unchanged
    expected = [3.0, 10.0, 12.0, 14.0, 16.0, 18.0, 20.0]
    assert result["capped"].tolist() == expected


def test_all_within_bounds():
    """All values within IQR bounds, no changes."""
    df = pd.DataFrame({"amount": [5, 10, 15, 20, 25]})
    result = cap_outliers_iqr(df, "amount", "capped")
    # Q1=10, Q3=20, IQR=10, LB=-5, UB=35
    assert result["capped"].tolist() == [5.0, 10.0, 15.0, 20.0, 25.0]


def test_missing_values():
    """Missing values become NA in capped column."""
    df = pd.DataFrame({"amount": [1, np.nan, 3, None, pd.NA, 100]})
    result = cap_outliers_iqr(df, "amount", "capped")
    # Valid values: [1,3,100] -> Q1=1, Q3=100, IQR=99, LB=-147.5, UB=248.5 -> no outliers
    # Capped: [1, NA, 3, NA, NA, 100]
    capped = result["capped"]
    assert capped.iloc[0] == 1.0
    assert pd.isna(capped.iloc[1])
    assert capped.iloc[2] == 3.0
    assert pd.isna(capped.iloc[3])
    assert pd.isna(capped.iloc[4])
    assert capped.iloc[5] == 100.0


def test_non_numeric_strings():
    """Non-numeric strings become NA."""
    df = pd.DataFrame({"amount": ["abc", "10", "20e", None]})
    # "10" is numeric, "abc" and "20e" are not
    result = cap_outliers_iqr(df, "amount", "capped")
    # After coerce: [NaN, 10, NaN, NaN] -> only 10 valid -> Q1=Q3=10, IQR=0, LB=10, UB=10
    # So capped: [NA, 10, NA, NA]
    capped = result["capped"]
    assert pd.isna(capped.iloc[0])
    assert capped.iloc[1] == 10.0
    assert pd.isna(capped.iloc[2])
    assert pd.isna(capped.iloc[3])


def test_empty_column_all_na():
    """Column with all missing values -> output all NA."""
    df = pd.DataFrame({"amount": [np.nan, None, pd.NA]})
    result = cap_outliers_iqr(df, "amount", "capped")
    assert result["capped"].isna().all()
    # also should have Float64 dtype
    assert result["capped"].dtype == pd.Float64Dtype()


def test_original_column_unchanged():
    """Original column should remain unchanged."""
    df = pd.DataFrame({"amount": [1, 2, 3, 4, 100]})
    original = df["amount"].copy()
    result = cap_outliers_iqr(df, "amount", "capped")
    assert result["amount"].equals(original)


def test_output_dtype():
    """Output column should be Float64 (nullable float)."""
    df = pd.DataFrame({"amount": [1, 2, 3]})
    result = cap_outliers_iqr(df, "amount", "capped")
    assert result["capped"].dtype == pd.Float64Dtype()


def test_integer_input():
    """Integer inputs produce float64 capped values."""
    df = pd.DataFrame({"amount": [10, 20, 30, 40, 200]})
    result = cap_outliers_iqr(df, "amount", "capped")
    # Q1=20, Q3=40, IQR=20, LB=-10, UB=100 -> 200 capped to 100
    assert result["capped"].iloc[4] == 100.0
    assert isinstance(result["capped"].iloc[4], float)


def test_all_identical_values():
    """All values identical -> no outliers, output same."""
    df = pd.DataFrame({"amount": [5, 5, 5, 5]})
    result = cap_outliers_iqr(df, "amount", "capped")
    # Q1=5, Q3=5, IQR=0, LB=5, UB=5 -> all values equal to bounds -> no change
    assert result["capped"].tolist() == [5.0, 5.0, 5.0, 5.0]


def test_single_row():
    """Single row DataFrame."""
    df = pd.DataFrame({"amount": [42]})
    result = cap_outliers_iqr(df, "amount", "capped")
    # Only one value, IQR=0 -> bounds equal to value
    assert result["capped"].iloc[0] == 42.0


def test_negative_values():
    """Negative values and negative outliers."""
    df = pd.DataFrame({"amount": [-50, -10, -5, 0, 5, 10, 100]})
    result = cap_outliers_iqr(df, "amount", "capped")
    # sorted: [-50, -10, -5, 0, 5, 10, 100] -> Q1=-10, Q3=10, IQR=20, LB=-40, UB=40
    # -50 capped to -40, 100 capped to 40, others unchanged
    expected = [-40.0, -10.0, -5.0, 0.0, 5.0, 10.0, 40.0]
    assert result["capped"].tolist() == expected


def test_large_dataframe_index_preservation():
    """Index is preserved in result."""
    df = pd.DataFrame({"amount": [1, 2, 3, 4, 100]}, index=[10, 20, 30, 40, 50])
    result = cap_outliers_iqr(df, "amount", "capped")
    assert list(result.index) == [10, 20, 30, 40, 50]


def test_output_column_name_custom():
    """Custom output column name."""
    df = pd.DataFrame({"val": [1, 2, 3, 4, 100]})
    result = cap_outliers_iqr(df, "val", "custom_capped")
    assert "custom_capped" in result.columns
    # check basic capping: Q1=2, Q3=4, IQR=2, LB=-1, UB=7 -> 100 capped to 7
    assert result["custom_capped"].iloc[4] == 7.0