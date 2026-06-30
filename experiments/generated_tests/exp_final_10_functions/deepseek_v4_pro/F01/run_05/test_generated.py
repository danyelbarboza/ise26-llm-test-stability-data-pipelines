import pytest
import pandas as pd
import numpy as np
from ise26.targets import clean_customer_names


def test_basic_normalization():
    df = pd.DataFrame({"customer_name": ["  João  Silva ", "MARÍA  ", None]})
    result = clean_customer_names(df)
    expected = pd.Series(
        ["joao silva", "maria", pd.NA], name="customer_name_clean"
    )
    pd.testing.assert_series_equal(result["customer_name_clean"], expected)


def test_default_output_column_name():
    df = pd.DataFrame({"customer_name": ["Alice"]})
    result = clean_customer_names(df)
    assert "customer_name_clean" in result.columns


def test_custom_output_column_name():
    df = pd.DataFrame({"customer_name": ["Bob"]})
    result = clean_customer_names(df, output_col="norm")
    assert "norm" in result.columns
    assert result["norm"].iloc[0] == "bob"


def test_custom_input_column_name():
    df = pd.DataFrame({"raw": ["Carol"]})
    result = clean_customer_names(df, name_col="raw", output_col="clean")
    assert "clean" in result.columns
    assert result["clean"].iloc[0] == "carol"


def test_preserves_original_dataframe():
    original_data = ["  João  Silva ", "MARÍA  ", None]
    df = pd.DataFrame({"customer_name": original_data.copy()})
    original_columns = df.columns.tolist()
    _ = clean_customer_names(df)
    assert df.columns.tolist() == original_columns
    assert df["customer_name"].tolist() == original_data


def test_returns_new_dataframe():
    df = pd.DataFrame({"customer_name": ["test"]})
    result = clean_customer_names(df)
    assert result is not df


def test_handles_leading_trailing_spaces():
    df = pd.DataFrame({"customer_name": ["   hello   ", "  world"]})
    result = clean_customer_names(df)
    expected = pd.Series(["hello", "world"], name="customer_name_clean")
    pd.testing.assert_series_equal(result["customer_name_clean"], expected)


def test_collapses_internal_whitespace():
    df = pd.DataFrame({"customer_name": ["a   b", "c\t \nd"]})
    result = clean_customer_names(df)
    expected = pd.Series(["a b", "c d"], name="customer_name_clean")
    pd.testing.assert_series_equal(result["customer_name_clean"], expected)


def test_lowercases():
    df = pd.DataFrame({"customer_name": ["MixedCase", "UPPER", "lower"]})
    result = clean_customer_names(df)
    expected = pd.Series(["mixedcase", "upper", "lower"], name="customer_name_clean")
    pd.testing.assert_series_equal(result["customer_name_clean"], expected)


def test_removes_accents():
    df = pd.DataFrame(
        {"customer_name": ["café", "niño", "São Paulo", "München"]}
    )
    result = clean_customer_names(df)
    expected = pd.Series(
        ["cafe", "nino", "sao paulo", "munchen"], name="customer_name_clean"
    )
    pd.testing.assert_series_equal(result["customer_name_clean"], expected)


def test_null_values_become_pd_na():
    df = pd.DataFrame({"customer_name": [None, np.nan, "valid"]})
    result = clean_customer_names(df)
    assert pd.isna(result["customer_name_clean"].iloc[0])
    assert pd.isna(result["customer_name_clean"].iloc[1])
    assert result["customer_name_clean"].iloc[2] == "valid"


def test_blank_string_maps_to_pd_na():
    df = pd.DataFrame({"customer_name": ["", "   ", "\t \n", "ok"]})
    result = clean_customer_names(df)
    assert pd.isna(result["customer_name_clean"].iloc[0])
    assert pd.isna(result["customer_name_clean"].iloc[1])
    assert pd.isna(result["customer_name_clean"].iloc[2])
    assert result["customer_name_clean"].iloc[3] == "ok"


def test_missing_input_column_raises():
    df = pd.DataFrame({"wrong": ["data"]})
    with pytest.raises(KeyError):
        clean_customer_names(df, name_col="customer_name")


def test_empty_dataframe():
    df = pd.DataFrame({"customer_name": []})
    result = clean_customer_names(df)
    assert list(result.columns) == ["customer_name", "customer_name_clean"]
    assert len(result) == 0
    assert result["customer_name_clean"].dtype == object


def test_column_order():
    df = pd.DataFrame({"id": [1], "customer_name": ["Alice"]})
    result = clean_customer_names(df)
    assert list(result.columns) == ["id", "customer_name", "customer_name_clean"]