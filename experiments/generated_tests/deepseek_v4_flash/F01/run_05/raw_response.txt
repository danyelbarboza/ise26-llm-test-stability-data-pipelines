import pandas as pd
import numpy as np
import pytest
from ise26.targets import clean_customer_names


def test_returns_new_dataframe():
    df = pd.DataFrame({"customer_name": ["Alice"]})
    result = clean_customer_names(df)
    assert result is not df
    assert "customer_name_clean" in result.columns
    assert list(result["customer_name_clean"]) == ["alice"]


def test_original_dataframe_unchanged():
    df = pd.DataFrame({"customer_name": ["Bob"]})
    original_copy = df.copy()
    clean_customer_names(df)
    pd.testing.assert_frame_equal(df, original_copy)


def test_normalize_name_lowercasing():
    df = pd.DataFrame({"name_col": ["UPPERCASE", "MixedCase", "lower"]})
    result = clean_customer_names(df, name_col="name_col", output_col="clean")
    assert list(result["clean"]) == ["uppercase", "mixedcase", "lower"]


def test_normalize_extra_spaces():
    df = pd.DataFrame({"customer_name": ["  John   Smith  ", "   Anne  "]})
    result = clean_customer_names(df)
    assert list(result["customer_name_clean"]) == ["john smith", "anne"]


def test_remove_accents():
    df = pd.DataFrame({"customer_name": ["José", "café", "François"]})
    result = clean_customer_names(df)
    assert list(result["customer_name_clean"]) == ["jose", "cafe", "francois"]


def test_null_values_become_na():
    df = pd.DataFrame({
        "customer_name": [None, np.nan, pd.NA, "Valid"]
    })
    result = clean_customer_names(df)
    expected = [pd.NA, pd.NA, pd.NA, "valid"]
    for i in range(3):
        assert pd.isna(result["customer_name_clean"].iloc[i]) is True
    assert result["customer_name_clean"].iloc[3] == "valid"


def test_blank_strings_become_na():
    df = pd.DataFrame({"customer_name": ["", "   ", "text"]})
    result = clean_customer_names(df)
    assert pd.isna(result["customer_name_clean"].iloc[0])
    assert pd.isna(result["customer_name_clean"].iloc[1])
    assert result["customer_name_clean"].iloc[2] == "text"


def test_mixed_blanks_and_nulls():
    df = pd.DataFrame({"customer_name": [pd.NA, "", "   ", "A B"]})
    result = clean_customer_names(df)
    for i in range(3):
        assert pd.isna(result["customer_name_clean"].iloc[i])
    assert result["customer_name_clean"].iloc[3] == "a b"


def test_duplicate_names_preserved():
    df = pd.DataFrame({"customer_name": ["Alice", "ALICE", "  alice  "]})
    result = clean_customer_names(df)
    assert list(result["customer_name_clean"]) == ["alice", "alice", "alice"]


def test_custom_column_names():
    df = pd.DataFrame({"raw": ["Test"]})
    result = clean_customer_names(df, name_col="raw", output_col="standard")
    assert "standard" in result.columns
    assert result["standard"].iloc[0] == "test"
    assert "raw" in result.columns


def test_non_string_types_preserved_in_other_columns():
    df = pd.DataFrame({
        "id": [1, 2],
        "customer_name": ["A", "B"]
    })
    result = clean_customer_names(df)
    assert list(result["id"]) == [1, 2]
    assert list(result["customer_name"]) == ["A", "B"]
    assert list(result["customer_name_clean"]) == ["a", "b"]