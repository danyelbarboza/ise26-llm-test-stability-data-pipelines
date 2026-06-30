import pandas as pd
import pytest

from ise26.targets import cap_outliers_iqr


def test_basic_outlier_capping():
    df = pd.DataFrame({"amount": [10, 12, 15, 14, 100, 13, 11, 200]})
    result = cap_outliers_iqr(df)

    expected_capped = [
        10.0,
        12.0,
        15.0,
        14.0,
        min(max(100.0, Q1 - 1.5 * (Q3 - Q1)), Q3 + 1.5 * (Q3 - Q1)),
        13.0,
        11.0,
        min(max(200.0, Q1 - 1.5 * (Q3 - Q1)), Q3 + 1.5 * (Q3 - Q1)),
    ]
    # compute actual bounds
    valid = pd.to_numeric(df["amount"], errors="coerce").dropna()
    Q1 = valid.quantile(0.25)
    Q3 = valid.quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    expected = valid.clip(lower=lower, upper=upper)
    expected_capped = pd.Series([pd.NA if pd.isna(v) else float(c) for v, c in zip(valid, expected)],
                                index=df.index, dtype="Float64")
    expected_capped.loc[~valid.isna()] = valid.clip(lower, upper).astype(float)
    expected_capped = expected_capped.astype("Float64")
    assert "amount_capped" in result.columns
    assert result["amount_capped"].equals(expected_capped)


def test_no_outliers():
    df = pd.DataFrame({"amount": [10, 12, 14, 13, 11, 15]})
    result = cap_outliers_iqr(df)
    expected = pd.Series([10.0, 12.0, 14.0, 13.0, 11.0, 15.0], dtype="Float64")
    assert result["amount_capped"].equals(expected)


def test_all_outliers():
    df = pd.DataFrame({"amount": [-1000, 1000, -2000, 2000]})
    result = cap_outliers_iqr(df)
    valid = pd.to_numeric(df["amount"], errors="coerce")
    Q1 = valid.quantile(0.25)
    Q3 = valid.quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    expected = valid.clip(lower=lower, upper=upper).astype(float)
    expected = expected.astype("Float64")
    assert result["amount_capped"].equals(expected)


def test_missing_values_stay_missing():
    df = pd.DataFrame({"amount": [10, None, 15, pd.NA, 20, np.nan]})
    result = cap_outliers_iqr(df)
    assert pd.isna(result.loc[1, "amount_capped"])
    assert pd.isna(result.loc[3, "amount_capped"])
    assert pd.isna(result.loc[5, "amount_capped"])
    assert result.loc[0, "amount_capped"] == 10.0
    assert result.loc[2, "amount_capped"] == 15.0
    assert result.loc[4, "amount_capped"] == 20.0


def test_non_numeric_values_become_na():
    df = pd.DataFrame({"amount": [10, "abc", 15.5, "def", 20]})
    result = cap_outliers_iqr(df)
    assert pd.isna(result.loc[1, "amount_capped"])
    assert pd.isna(result.loc[3, "amount_capped"])
    assert result.loc[0, "amount_capped"] == 10.0
    assert result.loc[2, "amount_capped"] == 15.5
    assert result.loc[4, "amount_capped"] == 20.0


def test_empty_dataframe():
    df = pd.DataFrame({"amount": []})
    result = cap_outliers_iqr(df)
    assert result["amount_capped"].tolist() == []
    assert result["amount_capped"].dtype == "Float64"


def test_constant_column_caps_any_deviation():
    df = pd.DataFrame({"amount": [5, 5, 5, 6, 5]})
    result = cap_outliers_iqr(df)
    # IQR = 0, bounds = 5. Any value !=5 becomes 5.
    expected_values = [5.0, 5.0, 5.0, 5.0, 5.0]
    expected = pd.Series(expected_values, dtype="Float64")
    assert result["amount_capped"].equals(expected)


def test_original_dataframe_unchanged():
    df = pd.DataFrame({"amount": [10, 100, 15]})
    original = df.copy()
    _ = cap_outliers_iqr(df)
    assert df.equals(original)
    # ensure no new column leaked to original
    assert "amount_capped" not in df.columns


def test_output_column_name_custom():
    df = pd.DataFrame({"amount": [10, 20, 200]})
    result = cap_outliers_iqr(df, output_col="capped_vals")
    assert "capped_vals" in result.columns
    assert "amount_capped" not in result.columns


def test_missing_column_raises():
    df = pd.DataFrame({"wrong": [1, 2, 3]})
    with pytest.raises(KeyError):
        cap_outliers_iqr(df)


def test_output_dtype_float64():
    df = pd.DataFrame({"amount": [7, 8, 9]})
    result = cap_outliers_iqr(df)
    assert result["amount_capped"].dtype == "Float64"