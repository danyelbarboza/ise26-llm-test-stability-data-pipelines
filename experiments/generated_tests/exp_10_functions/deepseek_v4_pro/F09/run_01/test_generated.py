import pandas as pd
import numpy as np
import pytest
from ise26.targets import cap_outliers_iqr


def test_basic_capping():
    df = pd.DataFrame({"amount": [1, 2, 3, 4, 100]})
    result = cap_outliers_iqr(df, value_col="amount", output_col="amount_capped")

    expected = pd.Series([1.0, 2.0, 3.0, 4.0, 7.0], name="amount_capped", dtype="Float64")
    pd.testing.assert_series_equal(result["amount_capped"], expected, check_names=False)
    # original column unchanged
    pd.testing.assert_series_equal(result["amount"], df["amount"])


def test_input_not_mutated():
    original = pd.DataFrame({"x": [5, 500, 10]})
    copy = original.copy(deep=True)
    cap_outliers_iqr(original, value_col="x", output_col="x_capped")
    pd.testing.assert_frame_equal(original, copy)


def test_result_is_new_dataframe():
    df = pd.DataFrame({"val": [1, 2, 3]})
    result = cap_outliers_iqr(df, value_col="val", output_col="val_capped")
    assert result is not df
    assert "val_capped" in result
    assert "val" in result


def test_missing_values_stay_missing():
    df = pd.DataFrame({"amount": [10, np.nan, 50, 1000, None]})
    result = cap_outliers_iqr(df)
    # Q1=30, Q3=525, IQR=495, lower=30-742.5=-712.5, upper=525+742.5=1267.5 → 1000 inside, 10 inside
    # caps: 10, 50, 1000 remain; NaN stays NaN
    expected = pd.Series([10.0, pd.NA, 50.0, 1000.0, pd.NA], name="amount_capped", dtype="Float64")
    pd.testing.assert_series_equal(result["amount_capped"], expected, check_names=False)


def test_invalid_non_numeric_become_na():
    df = pd.DataFrame({"val": ["a", "b", 1, 2.5, "3.0", None]})
    result = cap_outliers_iqr(df, value_col="val", output_col="val_capped")
    # numeric conversion: a,b become NaN; 1,2.5,3.0 are valid; None NaN
    # only 1,2.5,3.0 → Q1=2, Q3=2.75, IQR=0.75, lower=2-1.125=0.875, upper=2.75+1.125=3.875
    # all inside, caps = original coerced floats: 1.0, 2.5, 3.0
    expected = pd.Series([pd.NA, pd.NA, 1.0, 2.5, 3.0, pd.NA], name="val_capped", dtype="Float64")
    pd.testing.assert_series_equal(result["val_capped"], expected, check_names=False)


def test_all_missing_or_invalid():
    df = pd.DataFrame({"x": [np.nan, None, "abc"]})
    result = cap_outliers_iqr(df, value_col="x", output_col="x_capped")
    expected = pd.Series([pd.NA, pd.NA, pd.NA], name="x_capped", dtype="Float64")
    pd.testing.assert_series_equal(result["x_capped"], expected)


def test_no_outliers():
    df = pd.DataFrame({"n": [10, 12, 14, 16, 18]})
    result = cap_outliers_iqr(df, value_col="n", output_col="n_capped")
    pd.testing.assert_series_equal(result["n_capped"].astype(float), df["n"].astype(float), check_names=False)


def test_duplicate_values_preserved():
    df = pd.DataFrame({"v": [5, 5, 100, 100, 5]})
    result = cap_outliers_iqr(df, value_col="v", output_col="v_capped")
    # Q1=5, Q3=52.5, IQR=47.5, lower=5-71.25=-66.25, upper=52.5+71.25=123.75 → all inside
    expected = pd.Series([5.0, 5.0, 100.0, 100.0, 5.0], name="v_capped", dtype="Float64")
    pd.testing.assert_series_equal(result["v_capped"], expected, check_names=False)


def test_extreme_outliers_capped():
    df = pd.DataFrame({"data": [-1000, 0, 1, 2, 5000]})
    result = cap_outliers_iqr(df)
    # Q1=0.5, Q3=3.5, IQR=3, lower=0.5-4.5=-4, upper=3.5+4.5=8
    expected = pd.Series([-4.0, 0.0, 1.0, 2.0, 8.0], name="data_capped", dtype="Float64")
    pd.testing.assert_series_equal(result["data_capped"], expected, check_names=False)


def test_constant_column_no_variance():
    df = pd.DataFrame({"val": [7, 7, 7, 7]})
    result = cap_outliers_iqr(df, output_col="capped")
    # IQR=0, bounds=7 → all remain 7
    expected = pd.Series([7.0, 7.0, 7.0, 7.0], name="capped", dtype="Float64")
    pd.testing.assert_series_equal(result["capped"], expected)


def test_single_value():
    df = pd.DataFrame({"x": [42]})
    result = cap_outliers_iqr(df, value_col="x", output_col="capped")
    expected = pd.Series([42.0], name="capped", dtype="Float64")
    pd.testing.assert_series_equal(result["capped"], expected)


def test_custom_column_names():
    df = pd.DataFrame({"price": [1, 2, 3, 100]})
    result = cap_outliers_iqr(df, value_col="price", output_col="price_clean")
    assert "price_clean" in result
    assert "price" in result
    # Q1=2, Q3=51.5, IQR=49.5, lower=2-74.25=-72.25, upper=51.5+74.25=125.75 → 100 inside
    expected = pd.Series([1.0, 2.0, 3.0, 100.0], name="price_clean", dtype="Float64")
    pd.testing.assert_series_equal(result["price_clean"], expected, check_names=False)


def test_output_dtype_float64():
    df = pd.DataFrame({"a": [1, 2, 3]})
    result = cap_outliers_iqr(df)
    assert result["a_capped"].dtype.name == "Float64"


def test_empty_dataframe():
    df = pd.DataFrame({"amount": pd.Series([], dtype=float)})
    result = cap_outliers_iqr(df)
    assert list(result.columns) == ["amount", "amount_capped"]
    assert len(result) == 0
    assert result["amount_capped"].dtype.name == "Float64"


def test_index_preserved():
    df = pd.DataFrame({"v": [10, 20, 100]}, index=[5, 3, 1])
    result = cap_outliers_iqr(df)
    pd.testing.assert_index_equal(result.index, df.index)
    # Q1=15, Q3=60, IQR=45, lower=15-67.5=-52.5, upper=60+67.5=127.5 → all inside
    expected = pd.Series([10.0, 20.0, 100.0], index=[5, 3, 1], name="v_capped", dtype="Float64")
    pd.testing.assert_series_equal(result["v_capped"], expected)


def test_mixed_types_and_nulls():
    df = pd.DataFrame({"raw": [1, "2.5", np.nan, "invalid", 100, None]})
    result = cap_outliers_iqr(df, value_col="raw", output_col="clean")
    # numeric: 1, 2.5, 100 → Q1=2.5, Q3=51.25, IQR=48.75, lower=-70.625, upper=124.375 → all inside
    expected = pd.Series([1.0, 2.5, pd.NA, pd.NA, 100.0, pd.NA], name="clean", dtype="Float64")
    pd.testing.assert_series_equal(result["clean"], expected, check_names=False)


def test_negative_numbers_outliers():
    df = pd.DataFrame({"val": [-100, -2, 0, 2, 100]})
    result = cap_outliers_iqr(df)
    # Q1=-2, Q3=2, IQR=4, lower=-2-6=-8, upper=2+6=8 → cap -100 to -8, 100 to 8
    expected = pd.Series([-8.0, -2.0, 0.0, 2.0, 8.0], name="val_capped", dtype="Float64")
    pd.testing.assert_series_equal(result["val_capped"], expected, check_names=False)